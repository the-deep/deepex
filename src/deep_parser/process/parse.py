from fitz import Page
from anytree import NodeMixin

from ..const import MAX_ITERATION

from .divide import Set
from .section import Section

from ..utils.check import create_lines
from ..utils.text import get_page_text
from ..utils.search.sub import search_separations, pattern, partial_pattern


class DocumentTree(NodeMixin):
    
    def __init__(self, section, words, lines):
        
        super().__init__()
        
        if section.__class__ is Page:
            self.section = Section(rect=section.rect)
        else:
            self.section = section

        self.words = words
        self.lines = lines

    def get_text(self, images = None, output_format: str = "plain", p_num: int = 0):
        
        text = get_page_text(leaves=self.leaves, 
                             images=images, 
                             output_format=output_format, 
                             p_num=p_num)
        
        return text
    
def _get_element(pivot, words):
    
    w = pivot.get_words(words=words)
    l = create_lines(words=w)
    leaf = DocumentTree(section=pivot, words=w, lines=l)
    return leaf

def create_leaves(children, words):
    
    listTree = []
    for child in children:
        
        leaf = _get_element(pivot=child, words=words)
        listTree.append(leaf)
        
    return listTree


def add_leaves(root, group):
    
    main_words, add_children = root.words, []
    tree = group.tree
    
    if len(tree) == 1 and tree[0].__class__ is Set:
        
        group = tree[0]
        children = group.children
        sub_child = create_leaves(group.children, words=main_words)
        root.children = sub_child
        
    else:
        for section in tree:
            
            if section.__class__ is Section:
                
                child = _get_element(pivot=section, words=main_words)
                add_children.append(child)

            elif section.__class__ is Set:

                parent = section.parent.section if section.parent.section.rect != root.section.rect else root.section
                subparent = _get_element(pivot=parent, words=main_words)
                children = section.children
                subparent.children = create_leaves(children, words=subparent.words)
                add_children.append(subparent)

        root.children = add_children


def recursive_process(root, leaves = None, count=0):
    
    if root.leaves == leaves or count == MAX_ITERATION:
        return
    
    doc_dimension = root.section.rect
    old_leaves = root.leaves
    for leaf in old_leaves:
        search = pattern(section=leaf.section, words=leaf.words)
        if not search:
            searchorizontal = search_separations(section=leaf.section, lines=leaf.lines, page=doc_dimension)
            search = partial_pattern(section=leaf.section,
                                     words=leaf.words,
                                     horizontal=searchorizontal)            
        if search:
            group = Set(parent=leaf.section, section=search, recursion=True)
            add_leaves(leaf, group=group)
            
    count += 1
    return recursive_process(root, old_leaves, count)
