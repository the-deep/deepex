import os
import fitz
import json
import uuid
import typing
import string

from ..const import ERROR_MESSAGE_IN_TEXT
from ..attr import TEXT_BLOCK_TYPE, IMAGE_BLOCK_TYPE, TABLE_BLOCK_TYPE


class Block:
    
    def __init__(
        self,
        type: typing.Literal["image", "text", "table"],
        page: int,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        rect: typing.Tuple[float],
    ):
        
        self.type = type
        self.page = page
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.rect = rect
        
    def update(self, asdict):
        
        for k, v in asdict.items():
            if not hasattr(self, k):
                setattr(self, k, v)


class Pic:
    
    def __init__(self, name, rect, layout):
        
        self.name = name
        self.pic = layout.page.get_pixmap(
            clip=rect, 
            matrix=fitz.Matrix(2,2)
        )
        


def check_line(t):
    
    leng = len(t.strip().split())
    if leng == 1:
        new_string = t.translate(str.maketrans('', '', string.punctuation)).strip()
        if new_string.isalpha():
            return True
        else:
            return False
    elif leng > 1:
        return True


def return_error(page, raised_error):

    error_block = Block(
        type=TEXT_BLOCK_TYPE,
        page = page.number,
        x0=page.rect.x0,
        y0=page.rect.y0,
        x1=page.rect.x1,
        y1=page.rect.y1,
        rect=page.rect,        
    )

    error_block.update(
        {
            "text": str(raised_error),
            "textOrder": 0,
            "textCrop": None

        }
    )

    return [error_block], []


def get_data(leaves, images = None, p_num = 0, layout = None, document=None):
    
    
    images_words = [w.rect for im in images.imgs 
                    for w in im.words 
                    if im.skip_text is True]

    i, final, final_pic = 0, [], []    
    for leaf in leaves:
        
        leave = []
        for line in leaf.lines:
            if all(word.rect in images_words for word in line.line):
                t = ""
            else:
                t = " ".join([word.word for word in line.line])
            if t and check_line(t):
                leave.append(t)
            
        #if all(c == "" for c in leave):
        #    if leave:
        #        leave = [leave[0]]
        if leave:
            
            segment_text = " ".join([c for c in leave if c])
            
            text_block = Block(
                type=TEXT_BLOCK_TYPE,
                page=p_num,
                x0=leaf.section.x0,
                y0=leaf.section.y0,
                x1=leaf.section.x1,
                y1=leaf.section.y1,
                rect=tuple(leaf.section.rect),
            )
            
            value = leaf.lines
            x0, y0, x1, y1 = min(value, key=lambda x: x.xmin), min(value, key=lambda x: x.ymin), \
                             max(value, key=lambda x: x.xmax), max(value, key=lambda x: x.ymax)
                        
            text_block.update({
                "text": segment_text,
                "textOrder": i,
                "textCrop": (x0.xmin, y0.ymin, x1.xmax, y1.ymax)
            })
            
            final.append(text_block)
            i+=1
    
    for image in images.imgs:
        
        if image.is_table and image.words:
            
            table_block = Block(
                type=TABLE_BLOCK_TYPE,
                page=p_num,
                x0=image.xmin,
                y0=image.ymin,
                x1=image.xmax,
                y1=image.ymax,
                rect=tuple(image.rect)
            )
            
            name = f"table-{str(uuid.uuid4())}"
            table_block.update(
                {
                    "tableImageLink": f"{name}.png",
                    "tableCaption": "undefined",
                    "tableMeta": "undefined",
                    "tableText": "\n".join([" ".join(c.get_line_text()) 
                                            for c in image.lines])
                }
            )
            
            final.append(table_block)
            final_pic.append(Pic(
                name=name,
                rect=image.rect,
                layout=layout
            ))
        
        elif image.is_graph and image.skip_text:
            
            image_block = Block(
                type=IMAGE_BLOCK_TYPE,
                page=p_num,
                x0=image.xmin,
                y0=image.ymin,
                x1=image.xmax,
                y1=image.ymax,
                rect=tuple(image.rect)
            )
            
            name = f"pic-{str(uuid.uuid4())}"
            image_block.update(
                {
                    "imageLink": f"{name}.png",
                    "imageCaption": "undefined",
                    "imageMeta": "undefined",
                    "imageText": "\n".join([" ".join(c.get_line_text()) 
                                            for c in image.lines])
                }
            )
            
            final.append(image_block)
            final_pic.append(Pic(
                name=name,
                rect=image.rect,
                layout=layout
            ))
    
    if len(layout.page.get_images())>3000:
        pure_images = []
    else:
        pure_images = [layout.page.get_image_bbox(c[7]) 
                   for c in layout.page.get_images()]     
    
    for image in pure_images:
        
        image_block = Block(
                type=IMAGE_BLOCK_TYPE,
                page=p_num,
                x0=image.x0,
                y0=image.y0,
                x1=image.x1,
                y1=image.y1,
                rect=tuple(image)
            )
        
        name = f"pic-{str(uuid.uuid4())}"
        
        image_block.update(
            {
                "imageLink": f"{name}.png",
                "imageCaption": "undefined",
                "imageMeta": "undefined",
                "imageText": ""
            }
        )
        final.append(image_block)
        final_pic.append(Pic(
            name=name,
            rect=image,
            layout=layout
        ))
            
    return final, final_pic


class Response:
    
    class SubResponse:
        
        def __init__(self, blocks, metadata):
            self.blocks=blocks,
            self.metadata=metadata
            
    
    def __init__(
        self,
        blocks: list,
        document
    ):
        
        self.blocks = [block for page in blocks for block in page]
        self.metadata = document.metadata
        
    def to_json(self):
        
        b = json.loads(json.dumps(self.blocks, default=lambda o: o.__dict__))
        m = json.loads(json.dumps(self.metadata, default=lambda o: o.__dict__))
        return {"metadata": m, "blocks": b}
    
    def add_pics(self, pic_list):
        
        self.pics = pic_list
    
    def save_pics(self, directory_path: str = None):

        if directory_path:
            if not os.path.exists(directory_path):
                raise FileNotFoundError
            if not os.path.isdir(directory_path):
                raise NotADirectoryError
        else:
            directory_path = "./pics"
            os.mkdir(directory_path)

        for pic in self.pics:
            
            try:
                pic.pic.pil_save(os.path.join(directory_path, f"{pic.name}.png"))
            except (ValueError, Exception):
                continue