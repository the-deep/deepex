from itertools import groupby
from operator import attrgetter
from ..attr import START_PAGE_SEP, END_PAGE_SEP, PLAIN_SEP


def get_standard_text(lines, images=None, output_format="plain", p_num=0):
    
    excluded_words = []
    if images:
        if images.imgs:
            for im in images.imgs:
                if im.words: 
                    for c in im.words:
                        excluded_words.append(c.rect)
    
    total_text = [START_PAGE_SEP.format(p_num)]
    leave = []  
    for line in lines:
        
        if all(word.rect in excluded_words for word in line.line):
            t = []
        else:
            t = line.get_line_list()
        leave.append(t)
        
    plain = sorted([w for v in leave for w in v], key=attrgetter("blockn"))
    groups = [[i for i  in g] for _, g in groupby(plain, lambda x: x.__dict__["blockn"])]
    
    for c in groups:
        lines = " ".join([word.word for word in c]).split(". ")
        lines = "\n".join([c+"." if i+1!=len(lines) else c for i, c in enumerate(lines)])
        total_text.append(lines)
            
    if output_format == "plain":
        total_text = PLAIN_SEP.join(total_text)
        total_text = total_text + END_PAGE_SEP.format(p_num)
        return total_text
    elif output_format == "list":
        total_text = total_text + [END_PAGE_SEP.format(p_num)]
        return total_text
