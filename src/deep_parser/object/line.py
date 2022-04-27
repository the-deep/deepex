from fitz import Rect
from operator import attrgetter

from ..attr import *

class Line:

    def __init__(self, line):

        xmin, xmax = min(line, key=attrgetter(XMIN)), max(line, key=attrgetter(XMAX))
        ymin, ymax = min(line, key=attrgetter(YMIN)), max(line, key=attrgetter(YMAX))

        self.xmin, self.xmax, self.ymin, self.ymax = xmin.xmin, xmax.xmax, ymin.ymin, ymax.ymax
        self.rect = Rect(self.xmin, self.ymin, self.xmax, self.ymax)
        self.size = self.ymax - self.ymin
        self.line = sorted(line, key=attrgetter(XMIN))

    def get_line_text(self):
        return [c.word for c in self.line]

    def get_line_list(self):
        return self.line