from operator import attrgetter
from itertools import groupby

from ..attr import YMAX
from ..const import MIN_WORDS_IN_COLUMN
from ..object.line import Line
from ..object.word import ReWord


def create_lines(words, soft: bool = False):

    _vtext = sorted(words, key=attrgetter(YMAX))
    return [Line([c for c in g]) for _, g in groupby(map(ReWord, _vtext, [soft]*len(_vtext)))]


def intersection(words,
                 candidate,
                 vertical = True):

    if vertical:
        return True if [c for c in words if c.xmin <= candidate <= c.xmax] else False
    else:
        return True if [c for c in words if c.ymin <= candidate <= c.ymax] else False


def get_lines_distances(lines):
    return [round(nxt.ymin - curr.ymax, 0) for curr, nxt in zip(lines, lines[1:])]


def minumun_words(words, candidate, threshold = MIN_WORDS_IN_COLUMN):

    words_right = [c for c in words if c.xmin > candidate]

    if len(words_right) > threshold:
        return True
    else:
        return False

def columns_candidates(words,
                       separations):

    _separations = separations.copy()

    for curr, nxt, snxt in zip(_separations, _separations[1:], _separations[2:]):
        _words = [c for c in words if c.xmin > curr and c.xmax < snxt]
        if not minumun_words(_words, nxt):
            separations.remove(nxt)

    return separations
