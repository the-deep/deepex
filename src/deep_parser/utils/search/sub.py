from .vertical import search_vertical
from .horizontal import search_horizontal
from ...process.section import Section
from ...process.segment import Segment
from ...const import *



def search_separations(section,
                       page = None,
                       words = None,
                       lines = None):

    t_vertical, t_horizontal = None, None
    if words:
        t_vertical = search_vertical(words=words, section=section)
    if not lines:
        return t_vertical
    if lines:
        t_horizontal = search_horizontal(lines=lines, page=page, section=section)
    if not words:
        return t_horizontal

    return t_vertical, t_horizontal


def pattern(words,
            xmin = None, 
            ymin = None,
            xmax = None, 
            ymax = None,
            section = None):

    sub_section = section if section else Section(xmin, ymin, xmax, ymax)
    text = sub_section.get_words(words=words)
    vertical_candidates = search_separations(section=sub_section, words=text)
    if vertical_candidates:
        return Segment(section=sub_section, vertical=vertical_candidates)


def partial_pattern(section, words, horizontal):

    if not horizontal:
        return

    first = horizontal[:-1]
    reverse = horizontal[::-1][:-1]

    if first and section.rect.y0 != reverse[0].line_pos:

        sub_section = pattern(words=words,
                              xmin=section.rect.x0,
                              ymin=section.rect.y0,
                              xmax=section.rect.x1,
                              ymax=reverse[0].line_pos)

        if sub_section:
            return sub_section

    for line in first:

        sub_section = pattern(words=words, 
                              xmin=section.rect.x0,
                              ymin=line.line_pos,
                              xmax=section.rect.x1,
                              ymax=section.rect.y1)

        if sub_section:
            return sub_section

        for revline in reverse:

            if revline == line:
                break
            sub_section = pattern(words=words,
                                  xmin=section.rect.x0,
                                  ymin=line.line_pos,
                                  xmax=section.rect.x1,
                                  ymax=revline.line_pos)

            if sub_section:
                return sub_section

    return Segment(section=section, horizontal=horizontal)
