import fitz
from intervaltree import IntervalTree, Interval

def page_count(pdf_path):
    """
    Counts the number of pages in a PDF file
    """
    document = fitz.open(pdf_path)
    return int(document.pageCount)


def get_space(file_path, page_number = True):
    """
    Gets the height (in pt) of the biggest empty area on the last page.
    """
    document = fitz.open(file_path)
    lastPage = document[-1]

    tree_y = IntervalTree() # Heights of the empty spaces
    
    blocks = lastPage.getTextBlocks() # Read text blocks

    # Calculate CropBox and displacement
    disp = fitz.Rect(lastPage.CropBoxPosition, lastPage.CropBoxPosition)

    croprect = lastPage.rect + disp

    tree_y.add(Interval(croprect[1], croprect[3]))

    for b in blocks:
        r = fitz.Rect(b[:4]) # block rectangle
        r += disp

        _, y0, _, y1 = r
        tree_y.chop(y0,y1) # Takes away the non empty parts

    if not page_number:
        interval = max(tree_y)
        return interval[1] - interval[0]
    
    tree_y.remove(max(tree_y)) # Cannot optimize the space below the page number
    tree_y.remove(min(tree_y)) # Cannot optimize the space above the highest text block

    return max(i[1]-i[0] for i in tree_y)