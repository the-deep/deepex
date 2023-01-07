from collections import Counter
from ..attr import START_PAGE_SEP, END_PAGE_SEP, PLAIN_SEP


def exclude_repetitions(
    text_in_list: list, 
    check_thres: int = 2,
    exclude_thres: int = 5
    ):

    repetitions = sorted([(a, b) 
    for a, b in Counter([c.strip() 
    for i in text_in_list 
    for c in list(set(i[:check_thres]+i[-check_thres:]))]).items()], key=lambda x: x[1], reverse=True)

    exclude_rep = [c[0] for c in repetitions if c[1]>=exclude_thres]
    text_filtered = [[section for section in page if section not in exclude_rep] for page in text_in_list]

    return text_filtered


def reformat_text(total_text):

    replace_text = []
    
    for i, page in enumerate(total_text):   
        text = PLAIN_SEP.join(page)
        text = START_PAGE_SEP.format(i+1) + text + END_PAGE_SEP.format(i+1)
        replace_text.append(text)

    return "\n".join(replace_text)

def get_page_text(leaves, images = None, output_format = "plain", p_num = 0):
    
    excluded_words = []
    if images:
        if images.imgs:
            for im in images.imgs:
                if im.words: 
                    for c in im.words:
                        excluded_words.append(c.rect)

    #if output_format == "plain":
    #    total_text = [START_PAGE_SEP.format(p_num+1)]
    #elif output_format == "list":
    total_text = []
        
    for leaf in leaves:
        leave = []
        for line in leaf.lines:
            if all(word.rect in excluded_words for word in line.line):
                t = ""
            else:
                t = " ".join([word.word for word in line.line])
            #if len(t.strip().split()) > 1:
            if not len(t.strip().split())==1:
                if not t.strip().lower().isnumeric():
                    leave.append(t)
            
        #if all(c == "" for c in leave):
        #    if leave:
        #        leave = [leave[0]]
        if leave:
            t = " ".join([c for c in leave if c]).strip()
            if t: total_text.append(t)

    #print(total_text)
    #if output_format == "plain":
    #    total_text = PLAIN_SEP.join(total_text)
    #    total_text = total_text + END_PAGE_SEP.format(p_num+1)
    #    return total_text
    if output_format == "list":
        #total_text = total_text
        return total_text
