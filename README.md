## Deepex

### installation

`pip install git+https://github.com/the-deep/deepex`

### Usage



```
from deep_parser import TextFromFile


PDF_DOCUMENT = [YOUR_DOCUMENT_PATH]

with open(PDF_DOCUMENT_PATH,'rb') as f:
    binary = base64.b64encode(f.read())

document = TextFromFile(stream=binary, ext="pdf")
text, other = document.extract_text() 
```

`extract_text()` method returns a tupla with the extracted text and a `Results` class instance.
Output format can be selected with the output_format parameter: 
```
text, images = document.extract_text(output_format="list")
```
return list-formatted text. `Results` instance can be used for document images processing or saving, for example:

```
text, other = document.extract_text()
other.save_images(directory_path = DIRECTORY_PATH)
```

You can also extract text from webpages/html:

```
from deep_parser import TextFromWeb

URL = [WEBSITE_URL]
webpage = TextFromWeb(url=URL)
text = webpage.extract_text(output_format="list")

```
