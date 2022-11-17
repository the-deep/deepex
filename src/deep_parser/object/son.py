from ..process.section import Section
from ..process.segment import Segment


class Sons(Section):

    def __init__(self, segment, subsections = None):

        if segment.__class__ is Segment:
            self.section = segment.section
            self.subsections = segment.segments if segment.segments else segment.get_segments()
        else:
            self.section = segment
            self.subsections = subsections

        super().__init__(rect=segment.rect)
