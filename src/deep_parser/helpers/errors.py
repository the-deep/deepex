import threading

class DocumentProcessingError(Exception):
    def __init__(self, message: str = "Corrupted document"):
        super().__init__(message)
        
class ScannedDocumentError(Exception):
    def __init__(self, message: str = "Input Document is probably a scanned one, an OCR system is needed"):
        super().__init__(message)
