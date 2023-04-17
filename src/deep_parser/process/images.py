import fitz
import random
import timeout_decorator

from fitz import Rect
from typing import Union, List, Tuple

from ..const import MAX_WHILE, POINTS_MIN_DIFF, SKIP_TEXT
from ..object.word import Word, ReWord
from ..utils.check import create_lines

class Image:
    
    def __init__(self, 
                 page: int,
                 rect: Rect,
                 is_table: bool = False,
                 is_graph: bool = False):
        
        self.page = page
        self.xmin, self.ymin, self.xmax, self.ymax = rect
        self.rect = rect
        self.is_table = is_table
        self.is_graph = is_graph
        self.skip_text = True
        self.words = []
        self.lines = []
        
        
    @staticmethod
    def check_words(word: Union[Word, ReWord], 
                    ref: Rect):
        
        if word.xmin >= ref.x0 and word.ymin >= ref.y0 and word.xmax <= ref.x1 and word.ymax <= ref.y1:
            return True
        else:
            return False
        
    def get_words(self, page_words):
        
        self.words = [c for c in page_words if Image.check_words(c, self.rect)]
        if self.words:
            self.lines = create_lines(words=self.words)
            
        return self.words

    def wordsText(self):

        if self.words:
            return self.lines
    

class Images:
    
    def __init__(self,
                 page: fitz.fitz.Page,
                 page_words: List[Word]):
        
        self.page = page
        self.graphs = []
        self.imgs = self.process()
        [c.get_words(page_words) for c in self.imgs]
        self.refine()
    
    @staticmethod
    def check_inside(rect: Rect, 
                     ref: Rect):
        
        if rect.x0 >= ref.x0 and rect.y0 >= ref.y0 and rect.x1 <= ref.x1 and rect.y1 <= ref.y1:
            return True
        else:
            return False

    #@staticmethod
    #@func_set_timeout(10)
    @timeout_decorator.timeout(10)
    def inside(self, rect_list: List[Rect], check: bool = False):
        
        t = []
        for c in rect_list:
            if not [e for e in rect_list if Images.check_inside(c, e) and c != e]:
                t.append(c)
                if check:
                    double_check = [e for e in rect_list if Images.check_inside(e, c) and c!=e]
                    if double_check:
                        self.graphs.append(c)
    
        return t
    
    #@staticmethod
    def near(self, imgs):
        im = imgs.copy()
        try:
            res = self.remove_near_rect(imgs)
            return res
        except (timeout_decorator.TimeoutError, Exception) as e:
            return im
    
    @staticmethod
    def is_near(x: float, 
                y: float, 
                axis: str = "y"):
    
        thres = 1 if axis == "y" else 2

        if round(y) - thres <= round(x) <= round(y) + thres:
            return True
        else:
            return False
        
    @staticmethod
    def resize_zero_area(rect: Rect):
        
        x0, y0, x1, y1 = rect
        if abs(x0-x1)<POINTS_MIN_DIFF:
            x0, x1 = x0, x0+POINTS_MIN_DIFF
        elif abs(y0-y1)<POINTS_MIN_DIFF:
            y0, y1 = y0, y0+POINTS_MIN_DIFF
        
        return Rect(x0,y0,x1,y1)
        
    #@staticmethod 
    #@func_set_timeout(10)
    @timeout_decorator.timeout(10)
    def remove_near_rect(self, rect_list):
        
        """recursive method removing nearest graphical components"""
        
        t, f = {}, []
        rect_list = sorted(rect_list, key=lambda x: x.get_area(), reverse=True)
        for c in rect_list:
            if c in t.keys() or c in [s for a in t.values() for s in a]:
                continue
            t.update({c: []})
            for j in rect_list:
                if c==j: continue
                if Images.resize_zero_area(c).intersects(Images.resize_zero_area(j)):
                    t[c].append(j)

        if not [s for a in t.values() for s in a]:
            return rect_list
            
        for k, v in t.items():
            tot = list(set([k] + v))
            x0, y0, x1, y1 = min(tot, key=lambda x: x.x0), min(tot, key=lambda x: x.y0), \
                             max(tot, key=lambda x: x.x1), max(tot, key=lambda x: x.y1)
            
            rect = Rect(x0.x0, y0.y0, x1.x1, y1.y1)
            
            if len(tot)>1:
                self.graphs.append(rect)
                
            f.append(rect)
            
        return self.remove_near_rect(f)

    @staticmethod
    @timeout_decorator.timeout(10)
    def cleanup_coordinates(coo, _page):

        def zero_coordinate(c):

            return 0 if c < 0 else c

        def over_coordinate(coordinates, _page):

            _, __, xmax, ymax = _page.mediabox
            x0, y0, x1, y1 = coordinates
            if x1 > xmax:
                x1 = xmax
            if y1 > ymax:
                y1 = ymax
            return Rect(x0, y0, x1, y1)

        return over_coordinate(Rect(zero_coordinate(coo.x0),
                                    zero_coordinate(coo.y0),
                                    zero_coordinate(coo.x1),
                                    zero_coordinate(coo.y1)), _page)

    @staticmethod
    def remove_biggest(coors, _page, tabs):

        half_area = _page.rect.get_area() / 2
        for coo in coors:
            if coo not in tabs:
                if coo.get_area() > half_area:
                    coors.remove(coo)
        return coors
    
    @staticmethod
    @timeout_decorator.timeout(10)
    def _search_tables(imx0: Union[List[Tuple[Rect, str]], 
                                   List[Rect]],
                       axis: str = "y"):

        near, another = [], []
        imx0 = sorted(sorted([s for s in imx0], key=lambda x: x.x0), key=lambda x: x.y0)

        tot = list(set(imx0.copy()))
        call = {}

        if not tot:
            return call
        pivot = random.choice(tot)
        
        i, j, k = 1, 0, 0

        while tot and j <= MAX_WHILE:

            while True:
                k+=1
                if axis == "y":
                    near = [c for c in tot if (Images.is_near(pivot.y1, c.y0) 
                                               or Images.is_near(pivot.y0, c.y1)) and pivot != c]
                elif axis == "x":
                    near = [c for c in tot if (Images.is_near(pivot.x1, c.x0, axis="x") 
                                               or Images.is_near(pivot.x0, c.x1, axis="x")) and pivot != c]

                try:

                    if axis == "y":
                        another = [c for c in tot for b in call[str(i)] if (Images.is_near(b.y1, c.y0) 
                                                                            or Images.is_near(b.y0, c.y1)) and (b != c)]
                    elif axis == "x":
                        another = [c for c in tot for b in call[str(i)]
                                   if (Images.is_near(b.x1, c.x0, axis="x")
                                       or Images.is_near(b.x0, c.x1, axis="x"))
                                   and (b != c)]

                    near = list(set(near+another))

                except KeyError:
                    pass

                if not near:

                    if str(i) not in call.keys():
                        call.update({str(i): []})

                    try:
                        tot.remove(pivot)
                    except (IndexError, ValueError, KeyError):
                        pass

                    call[str(i)].append(pivot)                       
                    i += 1

                    try:
                        pivot = random.choice(tot)
                    except IndexError:
                        pass
                    break

                else:

                    if str(i) not in call.keys():
                        call.update({str(i): []})
                    for c in near:
                        tot.remove(c)
                        call[str(i)].append(c)

                    another = []    
                    call[str(i)].append(pivot)
                    pivot = random.choice(call[str(i)])
            j += 1

        return call
    
    
    def process(self):
        
        def tables(imgs):
            
            rex = []
            try:
                main_y_tables = Images._search_tables(imgs)
            except (timeout_decorator.TimeoutError, Exception) as e:
                main_y_tables = {}
            if main_y_tables:
                for _, a in main_y_tables.items():
                    try:
                        rex.append(Images._search_tables(a, axis="x"))
                    except (timeout_decorator.TimeoutError, Exception) as e:
                        pass
            return rex
        

        imgs_start = [self.cleanup_coordinates(c.get("rect"), self.page) for c in self.page.get_drawings()]
        #print(imgs_start)
        #imgs_start = Images.remove_biggest(imgs_start, self.page)
        imgs = list(set(self.inside(imgs_start, check=True)))
        #print("After", imgs)
        rex = tables(imgs)
        self.tabs = []
        #self.normal = []
        if rex:
            for el in rex:
                if el:
                    for value in el.values():
                        
                        x0, y0, x1, y1 = min(value, key=lambda x: x.x0), min(value, key=lambda x: x.y0), \
                                         max(value, key=lambda x: x.x1), max(value, key=lambda x: x.y1)
                        
                        rect = Rect(x0.x0, y0.y0, x1.x1, y1.y1)
                        
                        if len(value)>1:
                            self.tabs.append(rect)
                            
                        #elif len(value)==1:
                        #    self.normal.append(rect)
                            
                        imgs.append(rect)

        imgs = self.inside(list(set(imgs)), check=True)
        #imgs_tab = Images.inside(list(set(imgs_tab)))
        imgs = self.near(imgs)
        #imgs_tab = near(imgs_tab)
        imgs = Images.remove_biggest(imgs, self.page, self.tabs)
        
        final = []
        for c in list(set(imgs)):
            if c in self.tabs:
                final.append(Image(self.page.number, c, is_table=True))
            elif c in self.graphs:
                final.append(Image(self.page.number, c, is_graph=True))
            else:
                final.append(Image(self.page.number, c))
                
        return final
    
    def refine(self):
        for img in self.imgs:
            if img.is_table is False and img.words and img.is_graph is False:
                setattr(img, "skip_text", False)
            elif img.is_graph and img.words:
                setattr(img, "skip_text", True)
