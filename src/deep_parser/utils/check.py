from operator import attrgetter
from itertools import groupby

from ..attr import YMAX
from ..object.line import Line
from ..object.word import ReWord


def create_lines(words, soft: bool = False):

    _vtext = sorted(words, key=attrgetter(YMAX))
    return [Line([c for c in g]) for _, g in groupby(map(ReWord, _vtext, [soft]*len(_vtext)))]
