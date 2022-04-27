import statistics

from fitz import Rect

class BaseWord:

    def __init__(self, _word):

        if isinstance(_word, tuple):

            self.page, word_ = _word
            self.xmin, self.ymin, self.xmax, self.ymax, self.word, self.blockn, self.linen, self.wordn = word_
            self.rect = Rect(self.xmin, self.ymin, self.xmax, self.ymax)
            self.word_median = statistics.fmean([self.ymax, self.ymin])
            self.word_attr_list = list(self.__dict__.values())

        elif isinstance(_word, list):

            self.page, self.xmin, self.ymin, self.xmax, self.ymax, self.word, self.blockn, \
                    self.linen, self.wordn, self.rect, self.word_median = _word
            self.word_attr_list = list(self.__dict__.values())