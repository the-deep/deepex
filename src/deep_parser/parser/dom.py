from requests_html import HTMLSession
from ..dom.content import ContentParserFromWeb
from lxml.etree import SerialisationError


class TextFromWeb:

    def __init__(self, url):

        self.url = url
        self.session = HTMLSession()

    def _render_url(self):

        r = self.session.get(self.url, timeout=10)
        r.html.render(timeout=10, sleep=1, keep_page=True)
        return r

    def _get_html(self):

        try:
            results, = self._render_url()
        except (TimeoutError, Exception):
            results, = [self.session.get(self.url)]

        return results

    def extract_text(self, output_format: str = "plain"):

        results = self._get_html()
        try:
            self.pars = ContentParserFromWeb(url=self.url, html=results.html.html)
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
