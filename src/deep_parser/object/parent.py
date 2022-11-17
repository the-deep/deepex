from ..process.section import Section

class Parent(Section):

    def __init__(self, section):
        self.section = section
        super().__init__(rect=section.rect)