import re

TAG_SELECTOR = {
    "standard": {"tag": ["p", "li"], "classes": {}},
    "dhakatribune": {"tag": "div", "classes": {"class": "report-content"}}
}


regexps = {
    "unlikelyCandidates": re.compile(
        "combx|comment|community|disqus|extra|foot|header|menu|"
        "remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|"
        "pagination|pager|popup|tweet|twitter",
        re.I,
    ),
    "okMaybeItsACandidate": re.compile("and|article|article-content|page-article|body|column|col|main|shadow|app-documento-body", re.I),
    "positive": re.compile(
        "article|article-content|page-article|body|content|entry|hentry|main|page|pagination|post|text|"
        "blog|story|app-documento-body|report-content",
        re.I,
    ),
    "negative": re.compile(
        "combx|comment|com|contact|foot|footer|footnote|masthead|media|"
        "meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|"
        "shopping|tags|tool|widget",
        re.I,
    ),
    "extraneous": re.compile(
        "print|archive|comment|discuss|e[\-]?mail|share|reply|all|login|"
        "sign|single",
        re.I,
    ),
    "divToPElements": re.compile(
        "<(a|blockquote|dl|div|img|ol|p|pre|table|ul)", re.I
        #"<(a|blockquote|dl|img|ol|p|pre|table|ul)", re.I
    ),
    "replaceBrs": re.compile("(<br[^>]*>[ \n\r\t]*){2,}", re.I),
    "replaceFonts": re.compile("<(/?)font[^>]*>", re.I),
    "trim": re.compile("^\s+|\s+$", re.I),
    "normalize": re.compile("\s{2,}", re.I),
    "killBreaks": re.compile("(<br\s*/?>(\s|&nbsp;?)*)+", re.I),
    "videos": re.compile("http://(www\.)?(youtube|vimeo)\.com", re.I),
    "skipFootnoteLink": re.compile(
        "^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$", re.I
    ),
    "nextLink": re.compile("(next|weiter|continue|>([^\|]|$)|»([^\|]|$))", re.I),
    "prevLink": re.compile("(prev|earl|old|new|<|«)", re.I),
}
