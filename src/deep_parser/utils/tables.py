import re
import ast
import fitz

import pandas as pd
import numpy as np
import unicodedata

from fitz import Rect
from itertools import groupby
from collections import Counter
from ..process.layout import Layout
from ..process.section import Section
from ..utils.check import create_lines
from ..utils.search.vertical import search_vertical


class Draw:
    
    def __init__(self, rect):
        self.rect = rect
        self.x0, self.y0, self.x1, self.y1 = rect


class TableLineH(Draw):

    def __init__(self, item):
        super().__init__(item)
        
    def __eq__(self, other):

        return self.y0 - 1 <= other.y0 <= self.y0 + 1
    
class TableLineV(Draw):

    def __init__(self, item):
        super().__init__(item)
        
    def __eq__(self, other):
        

        return self.x0 - 1 <= other.x0 <= self.x0 + 1
    
class DataRow:
    
    def __init__(self, rect, cells):
        self.rect = rect
        self.cells = cells

def build_row_rect(row:list, intersect: list):
    list_ = []
    row = Rect(
        min(row, key=lambda x: x.x0).x0, min(row, key=lambda x: x.y0).y0,
        max(row, key=lambda x: x.x1).x1, max(row, key=lambda x: x.y0).y0
    )
    y0, y1 = row.y0, row.y1
    for c, c1 in zip(intersect, intersect[1:]):
        re = Rect(
                c.x0, y0, c1.x0, y1
            )
        if not Rect(int(re.x0), int(re.y0), int(re.x1), int(re.y1)).get_area()>0:
            continue
        list_.append(re)
    return DataRow(row, list_)


def get_words_median(words, section):
    text = [w for w in words if  section.rect.y0 <= w.word_median <= section.rect.y1 
            and w.xmin>=section.rect.x0 and w.xmax<=section.rect.x1]
    return text


def search_missing(true, other, threshold: int = 20):
    values = []
    for v in other:
        el = [c for c in true if abs(v-c)<=threshold]
        if el:
            min_el = min(el)
            if min_el not in values:
                values.append(min_el)
    #for c in values:
    miss = set(true).difference(values)
    indexes = [true.index(c) for c in miss]
    return indexes


def reshape_arab(x):
    try:
        if not any(["ARABIC" in unicodedata.name(c) for a in x for c in a]):
            return x
        find = re.compile(r'[\u0600-\u06ff\u0750-\u077f\ufb50-\ufbc1\ufbd3-\ufd3f\ufd50-\ufd8f\ufd50-\ufd8f\ufe70-\ufefc\uFDF0-\uFDFD]+')
        words = [c for c in re.split('[;|,|\-|\n|\|\/| ]', x) if c] 
        new_words = []
        for word in words:
            if find.match(word): 
                new_words.append(word[::-1]) 
            else:
                new_words.append(word)

        reversed_text = ' '.join(new_words)
        return reversed_text
    except Exception as e:
        return x


def cast_to_value(x):
    try:
        if x.isnumeric():
            x = ast.literal_eval(x)
    except (ValueError, SyntaxError, AttributeError):
        pass
    return x


class Tables:
    
    def __init__(self, document, tables_list, process_response):
        
        self.pdf = document
        self.tables = tables_list
        self.response = process_response
        
    def _get_rows(self, table_rect: Rect, table_drawings: list, threshold: int = 3):
        
        items_rect_filter_h = [c for c in table_drawings if abs(c.x1-c.x0)>=threshold]
        items_rect_filter_v = [c for c in table_drawings if abs(c.y1-c.y0)>=threshold]
        res_h = [[c for c in x] for _, x in groupby(map(TableLineH, sorted(items_rect_filter_h, key=lambda x: x.y0)))]
        res_v = [[c for c in x] for _, x in groupby(map(TableLineV, sorted(items_rect_filter_v, key=lambda x: x.x0)))]
        
        lh, lv, rows = [], [], []
        for c in res_h:
            x0, y0, x1, y1 = min(c, key=lambda x: x.x0), min(c, key=lambda x: x.y0), \
                         max(c, key=lambda x: x.x1), min(c, key=lambda x: x.y0)
            if round(table_rect.x0)-6 <= round(x0.x0) <= round(table_rect.x0)+6 and round(table_rect.x1)-6 <= round(x1.x1) <= round(table_rect.x1)+6:
                lh.append(Rect(x0.x0, y0.y0, x1.x1, y1.y0+0.1))

        lh.append(Rect(0, 0, table_rect.x1, 0.1))
        lh.append(Rect(0, table_rect.y1, table_rect.x1, table_rect.y1-0.1))

        for c in res_v:
            x0, y0, x1, y1 = min(c, key=lambda x: x.x0), min(c, key=lambda x: x.y0), \
                             min(c, key=lambda x: x.x0), max(c, key=lambda x: x.y1)
            lv.append(Rect(x0.x0, y0.y0, x0.x0+0.1, y1.y1))
            
            #if round(table_rect.x0)-1 <= round(x0.x0) <= round(table_rect.x0)+1 and round(table_rect.x1)-1 <= round(x1.x1) <= round(table_rect.x1)+1:
            #    l.append(Rect(x0.x0, y0.y0, x1.x1, y1.y0+0.1))

        lv.append(Rect(0, 0, 0.1, table_rect.y1))
        lv.append(Rect(table_rect.x1, 0, table_rect.x1-0.1, table_rect.y1))
    
        lv1 = sorted(list(set([Rect(round(a.x0), a.y0, a.x1, a.y1) for a in lv])), key=lambda x: x.x0)
        row = sorted(lh, key=lambda x: x.y0)
        
        for a, b in zip(row, row[1:]):
            row = [a, b]
            inter = [c for c in lv1 if int(c.y0)<=int(row[0].y0) and int(c.y1)>=int(row[1].y1)]
            datarow = build_row_rect(row, inter)
            rows.append(datarow)
            
        return rows
    
    
    def _get_total_rows(self, rows, threshold: int = 4):
        
        total, ver_total = [], []

        for row in rows:

            s = Section(rect=row.rect)
            w = get_words_median(Layout(self.tabPdf[0])._htext, s)
            vertical = search_vertical(w, threshold=4)

            if vertical: 
                ver_total.append(vertical)
                supp = []
                vertical_sep = [s.rect.x0] + vertical + [s.rect.x1]

                for a, b in zip(vertical_sep, vertical_sep[1:]):
                    words = [c for c in w if c.xmin>=a and c.xmax<=b]
                    supp.append(create_lines(words))
                if supp:
                    total.append((row,supp))
        
        return total, ver_total
    
    
    def _get_missing_values(self, total_rows, total_vertical_sep):
        
        self.most_com = Counter([len(c[1]) for c in total_rows]).most_common()[0][0]
        most_v = Counter([len(c) for c in total_vertical_sep]).most_common()[0][0]
        
        comm = [c for c in total_vertical_sep if len(c)==most_v]
        div = [c for c in total_vertical_sep if len(c)!=most_v]
        
        c1 = [c[1] for c in total_rows if len(c[1])==self.most_com]
        c2 = {i: c[1] for i, c in enumerate(total_rows) if len(c[1])!=self.most_com}
        
        mean_text_position_comm = []
        for element in c1:
            supp = []
            for  c in element:
                max_l = max(c, key=lambda x: x.xmax).xmax
                min_l = min(c, key=lambda x: x.xmin).xmin
                diffs = np.mean([max_l,min_l])
                supp.append(diffs)
            mean_text_position_comm.append(supp)
        
        self.mean_comm = np.mean(mean_text_position_comm, axis=0)

        for k, v in c2.items():
            supp = []
            for c in v:
                max_l = max(c, key=lambda x: x.xmax).xmax
                min_l = min(c, key=lambda x: x.xmin).xmin
                diffs = np.mean([max_l,min_l])
                supp.append(diffs)
            c2[k] = supp
            
        missing = {}
        for c in div:
            index = total_vertical_sep.index(c)
            miss = search_missing(list(np.mean(np.array(comm), axis=0)), c)
            missing.update({index: sorted(miss)})
            
        return missing, c2
    
    
    def get_table(self, idx: int, zoom: int = 5, save_pdf: bool = False, save_csv: bool =  False):
        
        self.tabPdf = fitz.Document()
        self.table = self.tables[idx]
        
        tab_rect = Rect(self.table.__dict__.get("rect"))
        tab_rect = Rect(
            tab_rect.x0-zoom, tab_rect.y0-zoom, tab_rect.x1+zoom, tab_rect.y1+zoom
        )
        
        self.tab_page = self.table.__dict__.get("page")
        self.pdf[self.tab_page].set_cropbox(tab_rect)
        self.tabPdf.insert_pdf(
            self.pdf, 
            from_page=self.tab_page, 
            to_page=self.tab_page)
        
        items = self.tabPdf[0].get_drawings()
        items_rect = [c.get("rect") for c in items]
        
        rows = self._get_rows(table_rect = self.tabPdf[0].rect, table_drawings=items_rect)
        total, ver_total = self._get_total_rows(rows=rows)
        missing, c2 = self._get_missing_values(total_rows=total, total_vertical_sep=ver_total)
        
        self.df = []
        for i, r in enumerate(total):
            _, c = r
            if i not in missing.keys():
                text = [reshape_arab(" ".join([" ".join(s.get_line_text()) for s in v])) for v in c]
                self.df.append(text)
            else:
                text = [reshape_arab(" ".join([" ".join(s.get_line_text()) for s in v])) for v in c]
                for m in missing.get(i):
                    if m>=len(c2.get(i)):
                        check = c2.get(i)[-1]
                    else:
                        check = c2.get(i)[m]
                    element_in_position = min([(i, abs(check-el)) for i, el in enumerate(self.mean_comm)],
                                              key=lambda x: x[1])
                    if element_in_position and m!=0:
                        if element_in_position[0]==m:
                            text.insert(m+1, "")
                    else: text.insert(m, "")
                    #text.insert(m, "")
                    if len(text)==self.most_com:
                        break
                self.df.append(text)

        
        dfp = pd.DataFrame(self.df)
        for c in dfp.columns:
            dfp[c] = [cast_to_value(x) for x in dfp[c].tolist()]
        
        self.df_pandas = dfp
        
        return self.df_pandas