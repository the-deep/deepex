from fitz import TEXT_PRESERVE_WHITESPACE, Rect
from ..attr import RECT, __TEXT__

def freeze_words(page):

    dict_text, final_text = page.get_text("dict", flags=TEXT_PRESERVE_WHITESPACE).get("blocks"), []
    for group in dict_text:
        lines = group.get("lines")
        for line in lines:
            x, y = line.get("dir")
            if (x == 0.0 and y == -1.0) or (x != 1.0 and y != 0.0) or line.get("wmode") != 0:
                final_text.append([{"rect": Rect(word.get("bbox")), "__text__": word.get("text")}
                                    for word in line.get("spans") if "text" in word.keys()])

    return [c for a in final_text for c in a]

def avoid_vertical_words(words, page):
    
    _, to_avoid = freeze_words(page), []
    for word in words:
        check = [c for c in _ if c.get(RECT).intersects(word[9]) and word[5] in c.get(__TEXT__)]
        if check:
            to_avoid.append(word)
    
    return to_avoid
