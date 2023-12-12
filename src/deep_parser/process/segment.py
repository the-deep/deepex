from operator import attrgetter

from .section import Section
from ..attr import SEPARATION_LINE_POSITION


class Segment:

    def __init__(self,
                 section,
                 vertical = None,
                 horizontal = None):

        if vertical and horizontal:
            raise ValueError("Only one direction at time is permitted")

        self.section = section
        self.vertical = Segment._get_sort(vertical) 
        self.horizontal = Segment._get_sort(horizontal)
        self.rect = section.rect 
        self.segments = []
        

    @staticmethod
    def _get_sort(separators_list):
        return sorted(separators_list, key=attrgetter(SEPARATION_LINE_POSITION)) if separators_list else []
    
    @staticmethod
    def _get_rect_coordinate(rect):
        y0, y1 = rect.y0, rect.y1
        x0, x1 = rect.x0, rect.x1
        return y0, y1, x0, x1        

    def get_segments(self):
        
        y0, y1, x0, x1 = Segment._get_rect_coordinate(self.rect)

        if self.vertical:

            for curr in self.vertical:
                self.segments.append(Section(x0, y0, curr.line_pos, y1))
                x0 = curr.line_pos

            self.segments.append(Section(x0, y0, x1, y1))

        elif self.horizontal:

            first, last = self.horizontal[0], self.horizontal[-1]

            if not first == last:
                self.segments.append(Section(x0, y0, x1, first.line_pos))
                for curr, nxt in zip(self.horizontal, self.horizontal[1:]):
                    self.segments.append(Section(x0, curr.line_pos, x1, nxt.line_pos))
                self.segments.append(Section(x0, last.line_pos, x1, y1))
            else:
                self.segments.append(Section(x0, y0, x1, first.line_pos))
                self.segments.append(Section(x0, first.line_pos, x1, y1))
                    
        return self.segments
