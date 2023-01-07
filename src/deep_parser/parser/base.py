import io
import os
import base64
import requests
import multiprocessing
from func_timeout import FunctionTimedOut

from ..const import ERROR_MESSAGE_IN_TEXT
from ..open.pdf import Pdf
from ..process.images import Images
from ..process.layout import Layout
from ..process.parse import DocumentTree, recursive_process
from ..utils.text import reformat_text, exclude_repetitions
        
class Results:

    def __init__(self, images, pages):

        if images and pages:
            self.attr = [(im, p) for im, p in zip(images, pages)]
        else:
            self.attr = None

    def save_images(self, directory_path: str = None):

        if not self.attr:
            return

        if directory_path:
            if not os.path.exists(directory_path):
                raise FileNotFoundError
            if not os.path.isdir(directory_path):
                raise NotADirectoryError
        else:
            directory_path = "./document_images"
            os.mkdir(directory_path)

        page_n = 0
        for imgs, lay in self.attr:

            pics = [lay.page.get_image_bbox(c[7]) for c in lay.page.get_images()]
            images = [c.rect for c in imgs]
            total = pics + images
            page_n += 1

            for i, im in enumerate(total):
                pix = lay.page.get_pixmap(clip=im)
                try:
                    pix.pil_save(os.path.join(directory_path, f"{page_n}_{i}.jpeg"))
                except (ValueError, Exception):
                    continue
    

class TextFromFile:

    def __init__(self, stream: bytes = None, from_web=False, url: str = None, ext: str = "pdf"):

        try:
            if from_web:
                if not url: raise ValueError("A valid PDF url must be passed")
                doc = requests.get(url).content
            stream = io.BytesIO(base64.b64decode(stream)) if not from_web else io.BytesIO(doc)
            self.pdf = Pdf(stream=stream, filetype=ext)
        except (RuntimeError, ValueError, Exception) as e:
            raise e
    
    def extract_text(self, output_format: str = "plain"):

        def _process_page(page, output_format: str = "plain"):
            
            try:
                _page = Layout(page)
                images = Images(page, page_words=_page._htext)
                root = DocumentTree(_page.page, _page._htext, _page._vtext)
                recursive_process(root=root)
                setattr(root, "number", _page.page.number)
                text = root.get_text(images=images, output_format="list", p_num=root.number)
                #if not text:
                #    text = root.get_text(output_format=output_format, p_num=root.number)
                return text, images.imgs, _page
            
            except (Exception, TimeoutError, FunctionTimedOut):
                text = ERROR_MESSAGE_IN_TEXT
                return text, [], _page
        
        _results = []
        for index in range(self.pdf.page_count):
            text, images, _page = _process_page(self.pdf.get_page(index), output_format="list")
            _results.append((text, images, _page))

        save, imgs, pages, i = [], [], [], 1
        for text, im, pg in _results:
            #text = p.get_text(images=im, output_format=output_format, p_num=i)
            save.append(text)
            imgs.append(im)
            pages.append(pg)
            i += 1

        save = exclude_repetitions(save)

        if output_format == "plain":
            results = reformat_text(save)#"\n".join(save)
        elif output_format == "list":
            results = save
        else:
            results = _results
        return results, Results(images=imgs, pages=pages)
        
    def extract_text_multi(self, output_format: str = "plain"):
        
        pdf = self.pdf
        global _process_page
        def _process_page(arg):
            
            page_idx, output_format = arg
            page = pdf[page_idx]
            _page = Layout(page)

            try:
                
                images = Images(page, page_words=_page._htext)
                root = DocumentTree(_page.page, _page._htext, _page._vtext)
                recursive_process(root=root)
                setattr(root, "number", _page.page.number)
                text = root.get_text(images=images, p_num=page_idx+1, output_format="list")

                return text, images.imgs, _page

            except (Exception, TimeoutError):
                text = ERROR_MESSAGE_IN_TEXT
                return text , [], _page
                
        indexes = [i for i in range(pdf.page_count)]
        pages = [pdf[i] for i in indexes]
        _format = ["list"]*len(indexes)
        arg = [(p, f) for p, f in zip(indexes, _format)]
        
        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
            results = p.map(_process_page, arg, chunksize=1)
        
        #text, imgs, pages = [c[0] for c in results], [c[1] for c in results], [c[2] for c in results]
        save, imgs, pages = [], [], []
        for text, im, pg in results:
            save.append(text)
            imgs.append(im)
            pages.append(pg)

        save = exclude_repetitions(save)

        if output_format == "plain":
            results = reformat_text(save)
        elif output_format == "list":
            results = save
        
        return results, Results(images=imgs, pages=pages)
    
    def get_chunk_size(self):
        if self.pdf.page_count > multiprocessing.cpu_count():
            return round(self.pdf.page_count/multiprocessing.cpu_count())
        else: return 1

    def get_document(self):
        return self.stream

    def get_extension(self):
        return self.ext

    def get_text(self):
        return self.text
