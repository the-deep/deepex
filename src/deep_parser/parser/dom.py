from requests_html import HTMLSession
from ..dom.content import ContentParserFromWeb
from lxml.etree import SerialisationError
from ..const import PDF_CONTENT_TYPE
from ..helpers.errors import ContentTypeError


class TextFromWeb:

    def __init__(self, url=None):

        self.url = url
        self.session = HTMLSession()

    def _render_url(self, url):

        r = self.session.get(url, timeout=10)
        content_type = r.headers.get('content-type')
        
        if PDF_CONTENT_TYPE in content_type:
            raise ContentTypeError
        else:
            r.html.render(timeout=10, sleep=1, keep_page=True, retries=2)
            return r

    def _get_html(self, url):

        try:
            results = self._render_url(url=url)
            return results
        except ContentTypeError:
            raise ContentTypeError
        except (TimeoutError, Exception) as e:
            r = self.session.get(url, timeout=10)
            content_type = r.headers.get('content-type')
            if PDF_CONTENT_TYPE in content_type:
                raise ContentTypeError
            else:
                results, = [r]
                return results

    def extract_text(self, url=None, output_format: str = "plain"):

        if hasattr(self, "url"):
            url = self.url
        elif url:
            url = url
        try:
            results = self._get_html(url=url)
        except ContentTypeError:
            self.close()
            raise ContentTypeError
        try:
            self.pars = ContentParserFromWeb(url=url, html=results.html.html)
        except (RecursionError, SerialisationError, Exception):
            return [""] if output_format == "list" else ""

        text = self.pars.get_content()

        if output_format == "plain":
            text = "\n".join(text)
        elif output_format == "list":
            text = [text]
        return text

    def close(self):
        self.session.close()
