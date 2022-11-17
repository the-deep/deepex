import fitz
from itertools import groupby
from operator import attrgetter

from ..attr import *
from ..utils.freeze import avoid_vertical_words
from ..object.base.page import BasePage
from ..object.base.line import BaseLines
from ..object.word import Word
from ..object.line import Line


class Layout:

    def __init__(self, page):

        self.page = page
        self.rect = page.rect

        pagetext = ([c for c in page.get_text_words(flags=fitz.TEXT_PRESERVE_WHITESPACE) if Layout._corrupted_coor(c)], page.number)
        
        vtext, htext = BasePage(pagetext).init_page(), BasePage(pagetext).init_page(position=1)
        
        avoid_vertical = avoid_vertical_words(words=htext, page=self.page)
        vtext, htext = [word for word in vtext if word not in avoid_vertical and word[5].strip()], \
                       [word for word in htext if word not in avoid_vertical]

        self._vtext = [Line([Word(w.word_attr_list) for w in g]) for _, g in groupby(map(BaseLines, vtext))]
        self._htext = sorted([word for line in self._vtext for word in line.get_line_list()], key=attrgetter(XMIN))


    @staticmethod
    def _corrupted_coor(word):
        
        c1, c2, c3, c4 = word[0], word[1], word[2], word[3]
        if all([c >= 0 for c in [c1, c2, c3, c4]]):
            return word
        else: return None
        
    def htext(self):
        return self._htext

    def vtext(self):
        return self._vtext
