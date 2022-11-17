import statistics

from operator import attrgetter
from ..check import intersection, columns_candidates
from ...object.separator import SeparationLine
from ...attr import SEPARATION_LINE_POSITION, XMAX
from ...const import VERTICAL_DIRECTION, VERTICAL_THRES_TOT, VERTICAL_THRES_CORR


def search_vertical(words,
                    threshold = VERTICAL_THRES_TOT,
                    double_check = VERTICAL_THRES_CORR,
                    section = None):


    columns_separation = []
    for curr, nxt in zip(words, words[1:]):
        if nxt.xmin - curr.xmax >= threshold:
            larger_value = [supp for supp in words[:words.index(curr)] if supp.xmax > curr.xmax]
            larger_value = sorted(larger_value, key=attrgetter(XMAX), reverse=True)[0] if larger_value else curr
            if nxt.xmin - larger_value.xmax > threshold*double_check:
                candidate = statistics.fmean([nxt.xmin, larger_value.xmax])
                if not intersection(words=words, candidate=candidate):
                    columns_separation.append(candidate)

    if section:

        columns_separation = columns_candidates(words=words,separations=columns_separation)
        columns_separation = sorted([SeparationLine(candidate=c, section=section, direction=VERTICAL_DIRECTION) for c in columns_separation],
                                    key=attrgetter(SEPARATION_LINE_POSITION))

    return columns_separation if columns_separation else None