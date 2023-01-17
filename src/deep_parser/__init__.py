from .parser.base import TextFromFile
from .parser.dom import TextFromWeb

def download_pypeeter_chromium():

    PLACEHOLDER_URL = "https://thedeep.io/"
    parser = TextFromWeb(url=PLACEHOLDER_URL)
    _ = parser.extract_text(output_format="list")
    parser.close()
    print("Chromium Downloaded")

#if __name__ == '__main__':
#    download_pypeeter_chromium()