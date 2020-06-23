import os
import shutil
import subprocess
import random

import fitz
from intervaltree import Interval, IntervalTree

def create_temporary_copy(path):
    tmp_path = os.path.join(os.getcwd(), "source")
    #Path(tmp_path).mkdir(parents=True, exist_ok=True)

    try:
        shutil.copytree(path, tmp_path)
        macro_path = os.path.join(os.getcwd(), "macros.tex")
        macro_copy_path = os.path.join(tmp_path, "macros.tex")
        shutil.copyfile(macro_path, macro_copy_path)
    except:
        pass

    return tmp_path

def get_variable_def(k, v):
    """
    \\defVal{name}{value}
    """
    if v == False:
        return ""
    if v == True:
        return fr"\defVal{{{k}}}{{}}"
    return fr"\defVal{{{k}}}{{{v}}}"


def write_variables(conf, tp):
    """ Write variables to file """

    with open(os.path.join(tp, "values.tex"), "w") as f:
        for k, v in conf.items():
            macro = get_variable_def(k, v)
            if macro != "":
                f.write(f"{macro}\n")


def compile_latex(filename):
    """
    1. Clean using latexmk
    2. Compile the LaTeX code using latexmk
    """

    working_directory, texfile = os.path.split(filename)

    command = ["latexmk", "-C", texfile]

    try:
        p1 = subprocess.Popen(
            command, cwd=working_directory,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            close_fds=True)
        p1.wait(timeout=15)

        command = ["latexmk", "-pdf", texfile]

        p2 = subprocess.Popen(
            command, cwd=working_directory,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            close_fds=True)

        p2.wait(timeout=15)

        # Clean up
        if p1 is not None:
            p1.kill()
        if p2 is not None:
            p2.kill()

        return True

    except subprocess.TimeoutExpired:
        return True

def page_count(pdf_path):
    """
    Counts the number of pages in a PDF file
    """
    document = fitz.open(pdf_path)
    return document.pageCount

def random_config(booleans = [], numbers = {}, enums = {}):
    """
    Generates a config dictionnary based on the range of values provided for each variable in the parameters.
    Booleans are either true or false and only their names need to be specified.
    Numbers are represented with the variable name as the key, and a tuple (min_val, max_val, precision) as the value.
    Enums are variables that can have one value from a list provided as the value in the dictionnary.
    """
    config = {}
    for boolean in booleans:
        config[boolean] = random.choice([True, False])

    for var_name, params in numbers.items():
        min, max, precision = params
        config[var_name] = round(random.uniform(min, max), precision)
    
    for var_name, choices in enums.items():
        config[var_name] = random.choice(choices)

    return config

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

    tree_y.remove(min(tree_y)) # Cannot optimize the space above the highest text block
    if page_number:
        tree_y.remove(max(tree_y)) # Cannot optimize the space under the page number
    print(tree_y)
    return max(i[1]-i[0] for i in tree_y)


if __name__ == "__main__":

    base_path = os.getcwd()
    document_path = os.path.join(base_path, "example", "fse")

    temp_path = create_temporary_copy(document_path)

    filename = "VaryingVariability-FSE15"
#    config = {
#        "PL_FOOTNOTE": True,
#        "ACK": True,
#        "PARAGRAPH_ACK": True,
#        "LONG_AFFILIATION": True,
#        "EMAIL": False,
#        "BOLD_ACK": False,
#        "LONG_ACK": False,
#
#        "vspace_bib": 4.32,
#        "bref_size": 0.85,
#        "cserver_size": 0.7,
#
#        "js_style": r"\tiny"
#    }
    config = random_config(
        booleans = ["PL_FOOTNOTE", "ACK", "PARAGRAPH_ACK", "LONG_AFFILIATION", "EMAIL", "BOLD_ACK", "LONG_ACK"],
        numbers = {
            "vspace_bib": (1, 5, 2),
            "bref_size": (0.7, 1, 2),
            "cserver_size": (0.6, 0.9, 2)
        },
        enums = {
            "js_style": [r"\tiny", r"\scriptsize", r"\footnotesize"]
        }
    )
    # config = {'PL_FOOTNOTE': True, 'ACK': False, 'PARAGRAPH_ACK': False, 'LONG_AFFILIATION': True, 'EMAIL': False, 'BOLD_ACK': True, 'LONG_ACK': False, 'vspace_bib': 4.77, 'bref_size': 1.0, 'cserver_size': 0.63, 'js_style': '\\scriptsize'}

    print(config)

    filename_tex = filename + ".tex"
    filename_pdf = filename + ".pdf"

    write_variables(config, temp_path)
    file_path = os.path.join(temp_path, filename_tex)

    compile_latex(file_path)
    shutil.copyfile(os.path.join(temp_path, filename_pdf), os.path.join(base_path, filename_pdf))

    shutil.rmtree(temp_path)