import statistics

from operator import attrgetter
from ..check import get_lines_distances, intersection
from ...object.separator import SeparationLine
from ..scores import custom_zscore
from ...const import *
from ...attr import SEPARATION_LINE_POSITION


def search_horizontal(lines, page, section):

    candidates, avoid_candidates = [], []
    section_area = section.rect.get_area()
    relative_area = section_area / page.get_area()

    differences = get_lines_distances(lines=lines)
    scores = custom_zscore(points=differences)

    words = [c for line in lines for c in line.get_line_list()]

    if len(scores) > 0:

        for prev, cur, nxt in zip(lines, lines[1:], lines[2:]):

            if prev in avoid_candidates: continue

            z_j, z_i = scores[lines.index(prev)], scores[lines.index(cur)]
            d_j, d_i = differences[lines.index(prev)], differences[lines.index(cur)]

            if not d_j or not d_i:
                d_j, d_i = d_j + RESCALE_MIN_DIFFERENCE, d_i + RESCALE_MIN_DIFFERENCE

            d_j = RESCALE_MIN_DIFFERENCE if d_j <= NULL else d_j
            d_i = RESCALE_MIN_DIFFERENCE if d_i <= NULL else d_i
            d_j, d_i = d_j / max(d_j, d_i), d_i / max(d_j, d_i)
            

            _up_latent = statistics.fmean([cur.ymin, prev.ymax])
            _down_latent = statistics.fmean([cur.ymax, nxt.ymin])

            _up_correction = HOR_CORRECTION if _up_latent in candidates else NULL
            _down_correction = HOR_CORRECTION if _down_latent in candidates else NULL

            _up_distance = abs(prev.size - cur.size) / max(prev.size, cur.size)
            _down_distance = abs(cur.size - nxt.size) / max(cur.size, nxt.size)

            _up = (FONTSIZE_MIN - relative_area) * (d_j + _up_distance) + relative_area * z_j - _up_correction
            _down = (FONTSIZE_MIN - relative_area) * (d_i + _down_distance) + relative_area * z_i - _down_correction

            if (z_j < HOR_THRES_TOT and z_i < HOR_THRES_TOT) and (_up_distance < FONTSIZE_DIFFERENCE and _down_distance < FONTSIZE_DIFFERENCE):
                continue
            elif _up > _down:
                candidates.append(_up_latent)
                avoid_candidates.append(cur)
            else:
                candidates.append(_down_latent)
                avoid_candidates.append(nxt)

        if candidates:

            separations = [c for c in candidates if not intersection(words, c, vertical=False)]
            separations = sorted([SeparationLine(candidate=c, section=section, direction=HORIZONTAL_DIRECTION) for c in list(set(separations))],
                                 key=attrgetter(SEPARATION_LINE_POSITION))
            return separations
