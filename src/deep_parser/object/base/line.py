from lib2to3.pytree import Base
from .word import BaseWord
from ...const import LINE_MEDIAN_THRESHOLD_LOW

class BaseLines(BaseWord):

    def __init__(self, _word):

        super().__init__(_word)

    def __eq__(self, other):

        return self.word_median - LINE_MEDIAN_THRESHOLD_LOW <= other.word_median <= self.word_median + LINE_MEDIAN_THRESHOLD_LOW