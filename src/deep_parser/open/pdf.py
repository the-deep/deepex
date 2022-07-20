import fitz
from fitz import Document

from ..const import DOCUMENT_LENGTH_THRES
from ..helpers.errors import ScannedDocumentError

fitz.TOOLS.mupdf_display_errors(False)
fitz.TOOLS.reset_mupdf_warnings()


class Pdf(Document):

    def __init__(self,
                 filename = None,
                 stream = None,
                 filetype = None,
                 rect = None,
                 width = 0,
                 height = 0,
                 fontsize = 11):

        super().__init__(filename=filename,
                         stream=stream,
                         filetype=filetype,
                         rect=rect,
                         width=width,
                         height=height,
                         fontsize=fontsize)
        
        self.filename = filename
        self.stream = stream
        self.filetype = filetype
        self.rect = rect
        self.width = width
        self.height = height
        self.fontsize = fontsize
        
        
        self.pages = [self.load_page(i) for i in range(self.page_count)]
        self.check_lenght()
        self.text = None
        
    def __reduce__(self):
        # we return a tuple of class_name to call,
        # and optional parameters to pass when re-creating
        return (self.__class__, (self.filename,
                                 self.stream, 
                                 self.filetype, 
                                 self.rect, 
                                 self.width,
                                 self.height,
                                 self.fontsize, ))

    def get_page(self, index):

        if index >= len(self.pages):
            raise IndexError(f"Document only has {len(self.pages)} page(s)")
        return self[index]
    
    def check_lenght(self):
        
        total_raw_text = " ".join([page.get_text("text") for page in self.pages]).strip().split()
        if len(total_raw_text)<=DOCUMENT_LENGTH_THRES:
            raise ScannedDocumentError
