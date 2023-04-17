from operator import itemgetter
from .word import BaseWord

class BasePage:

    def __init__(self, _page):

        self._page, self.page = _page

    def init_page(self, position = 4):

        return sorted([BaseWord((self.page, word)).word_attr_list for word in self._page], 
                      key=itemgetter(position))
    