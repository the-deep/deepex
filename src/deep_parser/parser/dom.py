import json
import requests
from ..const import PDF_CONTENT_TYPE
from ..helpers.errors import ContentTypeError
from trafilatura import extract, fetch_response


class ContentTypeError(Exception):
    def __init__(self, message: str = "Input Document is probably a PDF, not a HTML website!"):
        super().__init__(message)
        
        
class TextFromWeb:
    
    STATUSCODE200 = 200
    HEADERS = {"Content-Type": PDF_CONTENT_TYPE}
    TIMEOUT = 60000
    
    def __init__(self, url=None, selenium_ip: str = None):

        self.url = url
        self.selenium_ip = selenium_ip
        if self.selenium_ip:
            self.__check_status() == 200, ConnectionError("Selenium endpoint is not reachable")
            
    def __check_status(self):

        return requests.get(f"http://{self.selenium_ip}:8191/").status_code
    
    def __get_from_flaresolver(self, url):
        
        api_url = f"http://{self.selenium_ip}:8191/v1"
        response = requests.post(
            api_url, 
            headers=TextFromWeb.HEADERS,
            json={
                "cmd": "request.get",
                "url": url,
                "maxTimeout": TextFromWeb.TIMEOUT
            }
        )
        
        return response
    
    def _render_url(self, url):

        fetch = fetch_response(url, with_headers=True)
        
        if fetch:
            content_type = fetch.headers.get('content-type')

            if PDF_CONTENT_TYPE in content_type:
                raise ContentTypeError
                
        if fetch is None or fetch.status != 200:
            
            if not self.selenium_ip:
                raise Exception(f"Website {url} can't be rendered")
            
            try:
                fetch = self.__get_from_flaresolver(url=url)
                if fetch.status_code != 200:
                    raise TimeoutError(f"Error processing {url}: TimedOut")    
                response = fetch.json()["solution"]["response"]
                
            except Exception as e:
                raise Exception(f"Error processing {url}: {e}")
        else:
            response = fetch.data
                
        return response
        
    def _get_html(self, url):

        try:
            results = self._render_url(url=url)
            return results
        except Exception as e:
            raise e

    def extract_text(self, url=None, output_format: str = "plain"):

        if hasattr(self, "url") and self.url is not None:
            url = self.url
        elif url:
            url = url
        try:
            results = self._get_html(url=url)
        except Exception as e:
            raise e
        try:
            pars = json.loads(extract(results, output_format="json"))
        except Exception as e:
            raise Exception(f"Error extracting content from correctly rendered url: {self.url}")
            
        title, text = pars.get("title", ""), pars.get("text", "")

        if output_format == "plain":
            text = "\n".join([element for element in [title, text] if element])
        elif output_format == "list":
            text = [title, text]
        return text
