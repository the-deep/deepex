from operator import attrgetter

from ..attr import *
from .section import Section
from .segment import Segment
from ..helpers.errors import IntersectionsError


class Parent(Section):

    def __init__(self, section):
        self.section = section
        super().__init__(rect=section.rect)
        

class Sons(Section):

    def __init__(self, segment, subsections = None):

        if segment.__class__ is Segment:
            self.section = segment.section
            self.subsections = segment.segments if segment.segments else segment.get_segments()
        else:
            self.section = segment
            self.subsections = subsections

        super().__init__(rect=segment.rect)
        

class Set:

    """ set the structure of nested sections """

    def __init__(self,
                 parent,
                 children = None,
                 section = None,
                 subsections = None,
                 recursion: bool = False):

        if not parent.rect.intersects(section.rect):
            raise IntersectionsError 

        self.parent = Parent(parent)
        
        if section:
            self.section = section
            self.sons = Sons(segment=section, subsections=subsections)

        if children:
            self.children = children

        if recursion:
            self.tree = self._create_structure()

    def _create_structure(self):

        group = [self.parent, self.sons]
        
        __min__ = min(group, key=attrgetter(Y0))
        __max__ = max(group, key=attrgetter(Y1))
        __lmax__ = max(group, key=attrgetter(Y0))
        __umax__ = min(group, key=attrgetter(Y1))

        if (__min__ == __max__ == __umax__ == __lmax__) is True:

            total = [Set(parent=self.section.section, section=self.section.section, children=self.section.segments)]

        elif (__min__ == __max__ and __min__.__class__ is Parent) \
            and (__lmax__ == __umax__ and __lmax__.__class__ is Sons):

            first = Section(__min__.section.rect.x0,
                            __min__.section.rect.y0,
                            __min__.section.rect.x1,
                            self.sons.section.rect.y0)

            last = Section(__min__.section.rect.x0,
                           self.sons.section.rect.y1,
                           __min__.section.rect.x1,
                           __min__.section.rect.y1)

            child_group = Set(parent=self.section.section,
                              section=self.section.section,
                              children=self.section.segments)

            total = [first, child_group, last]

        elif (__min__ == __max__ == __umax__ and __min__.__class__ is Parent) \
            and __lmax__.__class__ is Sons:

            first = Section(__min__.section.rect.x0,
                            __min__.section.rect.y0,
                            __min__.section.rect.x1,
                            self.sons.section.rect.y0)

            child_group = Set(parent=self.section.section,
                              section=self.section.section,
                              children=self.section.segments)

            total = [first, child_group]

        elif (__min__ == __lmax__ == __max__ and __min__.__class__ is Parent) \
            and __umax__.__class__ is Sons:

            last = Section(__min__.section.rect.x0,
                           self.sons.section.rect.y1,
                           __min__.section.rect.x1,
                           __min__.section.rect.y1)

            child_group = Set(parent=self.section.section,
                              section=self.section.section,
                              children=self.section.segments)

            total = [child_group, last]
        else:

            total = [Set(parent=self.section.section, section=self.section.section, children=self.section.segments)]
        
        return total
