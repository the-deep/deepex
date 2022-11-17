from ..const import DIRECTION_LIST, VERTICAL_DIRECTION, HORIZONTAL_DIRECTION

class SeparationLine:

    def __init__(self, candidate, section, direction: str):

        assert direction in DIRECTION_LIST, ValueError
        if direction is VERTICAL_DIRECTION:
            self.ymin, self.ymax = section.rect.y0, section.rect.y1
            self.length = self.ymax - self.ymin
        elif direction is HORIZONTAL_DIRECTION:
            self.xmin, self.xmax = section.rect.x0, section.rect.x1
            self.length = self.xmax - self.xmin

        self.direction = direction
        self.section = section
        self.line_pos = candidate
