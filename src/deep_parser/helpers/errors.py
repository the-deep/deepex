class DocumentProcessingError(Exception):
    def __init__(self, message: str = "Corrupted document"):
        super().__init__(message)


class DLAError(Exception):
    def __init__(self, message: str = "DLA Failed"):
        super().__init__(message)
        
        
class IntersectionsError(Exception):
    def __init__(self, message: str = "Hierarchical Interesection Error"):
        super().__init__(message)
        
class ScannedDocumentError(Exception):
    def __init__(self, message: str = "Input Document is probably a scanned one, an OCR system is needed"):
        super().__init__(message)

class ContentTypeError(Exception):
    def __init__(self, message: str = "Input Document is probably a PDF, not a HTML website!"):
        super().__init__(message)
