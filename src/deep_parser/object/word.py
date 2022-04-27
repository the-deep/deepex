from ..const import LINE_MEDIAN_THRESHOLD, LINE_MEDIAN_THRESHOLD_LOW

class Word:

    def __init__(self, _word):

        self.page, self.xmin, self.ymin, self.xmax, self.ymax, self.word, self.blockn, \
            self.linen, self.wordn, self.rect, self.word_median = _word

        self.word = self.word.strip()
        self.size = self.ymax - self.ymin


class ReWord:

    def __init__(self, _word: Word, soft: bool = False):

        self.page, self.xmin, self.ymin, self.xmax, self.ymax, self.word, self.blockn, \
            self.linen, self.wordn, self.rect, self.word_median, self.size = tuple(_word.__dict__.values())

        self.soft = soft

    def __eq__(self, other):

        thres = LINE_MEDIAN_THRESHOLD if self.soft else LINE_MEDIAN_THRESHOLD_LOW
        return round(self.word_median) - thres <= round(other.word_median) <= round(self.word_median) + thres