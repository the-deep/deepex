"""
Inspired by readable-content package
author="Nabin Khadka",
author_email="nbnkhadka14@gmail.com",
license="MIT license",
description="Collect actual content of any article, blog, news, etc.",
url="https://github.com/nabinkhadka/readable-content",

LICENSE:
Copyright (c) readable-content developers.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

import re
import math
import posixpath
# from turtle import ht
import urllib.parse
import urllib.request

from html import unescape
from bs4 import BeautifulSoup
from lxml import etree as ET
from lxml.html import fromstring
from ..dom.regexps import regexps


class ContentParserFromWeb:

    # _RE_COMBINE_WHITESPACE = re.compile(r"\s+")

    def __init__(self, url, html=None):

        self.candidates = {}
        self.input = html
        self.regexps = regexps
        if html is None:
            self.input = urllib.request.urlopen(url).read().decode("utf-8")
        self.url = url
        self.input = self.regexps["replaceBrs"].sub("</p><p>", self.input)
        self.input = self.regexps["replaceFonts"].sub("<\g<1>span>", self.input)

        self.html = BeautifulSoup(self.input, "lxml")
        self.remove_script()
        self.remove_style()
        self.remove_link()

        self.title = unescape(self.get_article_title())
        self.content = self.grab_article()
        
    @staticmethod
    def clean_newline(html_string):
        
        html_string = re.sub(re.compile(r"(?:<p>|<p)\n+"), "<p>", html_string)
        html_string = re.sub(re.compile(r"\n<\/p>"), "</p>", html_string)
        
        return html_string

    def get_content(self):

        if not self.content:
            return ""

        html_string = ContentParserFromWeb.clean_newline(ET.tostring(fromstring(self.content)).decode("utf-8"))
        self._html = html_string
        
        text_only = re.sub(re.compile(r"<.*?>"), "", html_string)
        self.group = [c.groupdict() for c in 
                      re.finditer(r"(?:(?P<img><img(.+?)\/>)|(?P<txt><(?:p|h1|h2|h3|h4|h5)(?:>|(.+?)>)(?s:.*?)<\/(?:p|h1|h2|h3|h4|h5)>))", html_string)]
        
        # cleaned_text = text_only.replace("\n\n", " ").replace("\n", " ")
        text = [unescape(c).strip() for c in text_only.strip().split(".\n") if c]
        total = [self.title.strip()] + text
        return total

    def remove_script(self):
        for elem in self.html.findAll("script"):
            elem.decompose()

    def remove_style(self):
        for elem in self.html.findAll("style"):
            elem.decompose()

    def remove_link(self):
        for elem in self.html.findAll("link"):
            elem.decompose()

    def grab_article(self):

        for elem in self.html.findAll(True):
            unlikely_match_string = " ".join(elem.get("id", "")) + " ".join(
                elem.get("class", "")
            )

            if (
                    self.regexps["unlikelyCandidates"].search(unlikely_match_string)
                    and not self.regexps["okMaybeItsACandidate"].search(unlikely_match_string)
                    and elem.name != "body"
            ):  
                
                elem.extract()
                continue

            if elem.name == "div":
                #print("##############################################\n")
                #print(f"{unlikely_match_string}-------------->\n {elem}")
                #print("\n############################################\n")
                s = elem.renderContents().decode("utf-8")
                #print("SSSSSSSSSSSSSSSS", s)
                if not self.regexps["divToPElements"].search(s):
                    elem.name = "p"
        
        for node in self.html.findAll("p"):
            # print("NOOOODE", node)
            parent_node = node.parent
            grand_parent_node = parent_node.parent
            inner_text = node.text

            if not parent_node or len(inner_text) < 20:
                continue

            parent_hash = hash(str(parent_node))
            grand_parent_hash = hash(str(grand_parent_node))

            if parent_hash not in self.candidates:
                self.candidates[parent_hash] = self.initialize_node(parent_node)

            if grand_parent_node and grand_parent_hash not in self.candidates:
                self.candidates[grand_parent_hash] = self.initialize_node(
                    grand_parent_node
                )
            content_score = 1
            content_score += inner_text.count(",")
            content_score += inner_text.count(u"，")
            content_score += min(math.floor(len(inner_text) / 100), 3)

            self.candidates[parent_hash]["score"] += content_score
            if grand_parent_node:
                self.candidates[grand_parent_hash]["score"] += content_score / 2

        top_candidate = None
        self.top = top_candidate

        for key in self.candidates:
            self.candidates[key]["score"] = self.candidates[key]["score"] * (
                    1 - self.get_link_density(self.candidates[key]["node"])
            )

            if (
                    not top_candidate
                    or self.candidates[key]["score"] > top_candidate["score"]
            ):
                top_candidate = self.candidates[key]

        content = ""
        if top_candidate:
            content = top_candidate["node"]
            content = self.clean_article(content)
        return content

    def clean_article(self, content):

        self.clean_style(content)
        self.clean(content, "h1")
        self.clean(content, "object")
        self.clean_conditionally(content, "form")

        if len(content.findAll("h2")) == 1:
            self.clean(content, "h2")

        self.clean(content, "iframe")

        self.clean_conditionally(content, "table")
        self.clean_conditionally(content, "ul")
        self.clean_conditionally(content, "div")

        self.fix_images_path(content)
        
        
        content = content.renderContents().decode("utf-8")
        content = self.regexps["killBreaks"].sub("<br />", content)

        return content

    def clean(self, e, tag):

        target_list = e.findAll(tag)
        is_embed = 0
        if tag == "object" or tag == "embed":
            is_embed = 1

        for target in target_list:
            attribute_values = ""
            for attribute in target.attrs:
                try:
                    # import pdb;pdb.set_trace()
                    if type(target[attribute]) == list:
                        for c in target[attribute]:
                            attribute_values += c
                    else:
                        attribute_values += target[attribute]
                except KeyError:
                    import pdb

                    pdb.set_trace()
                    print("")

            if is_embed and self.regexps["videos"].search(attribute_values):
                continue

            if is_embed and self.regexps["videos"].search(
                    target.renderContents(encoding=None)
            ):
                continue
            target.extract()

    @staticmethod
    def clean_style(e):

        for elem in e.findAll(True):
            del elem["class"]
            del elem["id"]
            del elem["style"]

    def clean_conditionally(self, e, tag):
        tags_list = e.findAll(tag)

        for node in tags_list:
            weight = self.get_class_weight(node)
            hash_node = hash(str(node))
            if hash_node in self.candidates:
                content_score = self.candidates[hash_node]["score"]
            else:
                content_score = 0

            if weight + content_score < 0:
                node.extract()
            else:
                p = len(node.findAll("p"))
                img = len(node.findAll("img"))
                li = len(node.findAll("li")) - 100
                _input = len(node.findAll("input"))
                embed_count = 0
                embeds = node.findAll("embed")
                for embed in embeds:
                    if not self.regexps["videos"].search(embed["src"]):
                        embed_count += 1
                link_density = self.get_link_density(node)
                content_length = len(node.text)
                to_remove = False

                if img > p:
                    to_remove = True
                elif li > p and tag != "ul" and tag != "ol":
                    to_remove = True
                elif _input > math.floor(p / 3):
                    to_remove = True
                elif content_length < 25 and (img == 0 or img > 2):
                    to_remove = True
                elif weight < 25 and link_density > 0.2:
                    to_remove = True
                elif weight >= 25 and link_density > 0.5:
                    to_remove = True
                elif (embed_count == 1 and content_length < 35) or embed_count > 1:
                    to_remove = True

                if to_remove:
                    #pass
                    node.extract()

    def get_article_title(self):
        title = ""
        try:
            title = self.html.find("title").text
        except (Exception, KeyError, ValueError):
            pass

        return title

    def initialize_node(self, node):
        content_score = 0

        if node.name == "div":
            content_score += 5
        elif node.name == "blockquote":
            content_score += 3
        elif node.name == "form":
            content_score -= 3
        elif node.name == "th":
            content_score -= 5

        content_score += self.get_class_weight(node)

        return {"score": content_score, "node": node}

    def get_class_weight(self, node):
        weight = 0
        if "class" in node:
            if self.regexps["negative"].search(node["class"]):
                weight -= 25
            if self.regexps["positive"].search(node["class"]):
                weight += 25

        if "id" in node:
            if self.regexps["negative"].search(node["id"]):
                weight -= 25
            if self.regexps["positive"].search(node["id"]):
                weight += 25

        return weight

    @staticmethod
    def get_link_density(node):
        links = node.findAll("a")
        text_length = len(node.text)

        if text_length == 0:
            return 0
        link_length = 0
        for link in links:
            link_length += len(link.text)

        return link_length / text_length

    def fix_images_path(self, node):
        imgs = node.findAll("img")
        for img in imgs:
            src = img.get("src", None)
            if not src:
                img.extract()
                continue

            if "http://" != src[:7] and "https://" != src[:8]:

                new_src = urllib.parse.urljoin(self.url, src)
                new_src_arr = urllib.parse.urlparse(new_src)
                new_path = posixpath.normpath(new_src_arr[2])
                new_src = urllib.parse.urlunparse(
                    (
                        new_src_arr.scheme,
                        new_src_arr.netloc,
                        new_path,
                        new_src_arr.params,
                        new_src_arr.query,
                        new_src_arr.fragment,
                    )
                )
                img["src"] = new_src
