from fitz import Rect

class Section:

    def __init__(self, xmin = None, ymin = None, xmax = None, ymax = None, rect = None):

        self.rect = Rect(xmin, ymin, xmax, ymax) if not rect else rect
        self.x0, self.y0, self.x1, self.y1 = self.rect
        self.text = None

    def _is_in(self, w):

        if w.rect.x0 > self.rect.x0 and w.rect.x1 < self.rect.x1 and w.rect.y0 > self.rect.y0 and w.rect.y1 < self.rect.y1:
            return True
        else:
            return False

    def get_words(self, words):
        self.text = [w for w in words if self._is_in(w)]
        return self.text
