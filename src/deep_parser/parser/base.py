import io
import os
import base64
import multiprocessing

from ..const import ERROR_MESSAGE_IN_TEXT
from ..open.pdf import Pdf
from ..process.images import Images
from ..process.layout import Layout
from ..utils.text import get_standard_text
        
        
        
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
            images = [c.rect for c in imgs.imgs]
            total = pics + images
            page_n += 1

            for i, im in enumerate(total):
                pix = lay.page.get_pixmap(clip=im)
                try:
                    pix.pil_save(os.path.join(directory_path, f"{page_n}_{i}.jpeg"))
                except (ValueError, Exception):
                    continue
                

class TextFromFile:

    def __init__(self, stream: bytes, ext: str):

        try:
            self.pdf = Pdf(stream=io.BytesIO(base64.b64decode(stream)), filetype=ext)
        except (RuntimeError, ValueError, Exception) as e:
            raise e
    
    def serial_extract_text(self, output_format: str = "plain"):

        def process(page):
            
            _page = Layout(page)
            images = Images(page, page_words=_page._htext)

            return images, _page
        
        _results = []
        for index in range(self.pdf.page_count):
            images, _page = process(self.pdf.get_page(index))
            _results.append((images,_page))

        save, imgs, pages, i = [], [], [], 1
        for im, pg in _results:

            text = get_standard_text(lines= pg._vtext, images=im, output_format=output_format, p_num=i)
            save.append(text)
            imgs.append(im)
            pages.append(pg)
            i += 1

        if output_format == "plain":
            results = "\n".join(save)
        elif output_format == "list":
            results = save
        else:
            results = _results
        return results, Results(images=imgs, pages=pages)
        
    def extract_text(self, output_format: str = "plain"):
        
        pdf = self.pdf
        global _process_page
        def _process_page(arg):
            
            page_idx, output_format = arg
            page = pdf[page_idx]
            _page = Layout(page)

            try:
                
                images = Images(page, page_words=_page._htext)
                text = get_standard_text(lines=_page._vtext, images=images, p_num=page_idx+1, output_format=output_format)
                return text, images.imgs

            except Exception as e:
                text = ERROR_MESSAGE_IN_TEXT
                return text , []
                
        indexes = [i for i in range(pdf.page_count)]
        pages = [pdf[i] for i in indexes]
        _format = [output_format]*len(indexes)
        arg = [(p, f) for p, f in zip(indexes, _format)]
        
        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
            results = p.map(_process_page, arg, chunksize=1)
        
        text, imgs = [c[0] for c in results], [c[1] for c in results]
        text = "\n".join(text) if output_format == "plain" else text
        result_imgs = Results(images=imgs, pages=pages)
        
        return text, result_imgs
    
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
