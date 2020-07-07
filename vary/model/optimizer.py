import os
import shutil
import subprocess
import random
import json

import fitz
from intervaltree import Interval, IntervalTree

import vary.model.decision_trees.analysis as dt_al

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

def generate_bbl(filename):
    """
    Loads the bibliography file
    """
    working_directory, texfile = os.path.split(filename)
    
    try:
        # Precompile the main file to get the .aux file
        command = ["pdflatex", "-draftmode", "-interaction=batchmode", texfile + ".tex"]
        p1 = subprocess.Popen(
            command, cwd=working_directory,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            close_fds=True)
        p1.wait(timeout=15)

        # Load the bibtex references from the .aux
        command = ["bibtex", texfile + ".aux"]
        p2 = subprocess.Popen(
            command, cwd=working_directory,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            close_fds=True)
        p2.wait(timeout=15)

        if p1 is not None:
            p1.kill()
        if p2 is not None:
            p2.kill()

    except subprocess.TimeoutExpired:
        pass


def compile_latex(filename):
    """
    1. Clean using latexmk
    2. Compile the LaTeX code using latexmk
    """

    working_directory, texfile = os.path.split(filename)

    try:

        # Compile the document
        command = ["pdflatex", "-interaction=batchmode", texfile]
        
        p3 = subprocess.Popen(
            command, cwd=working_directory,
            stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            close_fds=True)

        p3.wait(timeout=15)

        
        if p3 is not None:
            p3.kill()

        return True

    except subprocess.TimeoutExpired:
        return True

def page_count(pdf_path):
    """
    Counts the number of pages in a PDF file
    """
    document = fitz.open(pdf_path)
    return int(document.pageCount)

def random_config(conf_source):
    """
    Generates a config dictionnary based on the range of values provided from a dictionnary containing the following keys :
    "booleans", "numbers", "enums" and "choices".
    Booleans are either true or false and only their names need to be specified.
    Numbers are represented with the variable name as the key, and a tuple (min_val, max_val, precision) as the value.
    Enums are variables that can have one value from a list provided as the value in the dictionnary.
    Choices are groups of booleans where exactly one can be true at a time. They are provided as a list of lists.
    """
    config = {}
    if "booleans" in conf_source:
        for boolean in conf_source["booleans"]:
            config[boolean] = random.choice([True, False])

    if "numbers" in conf_source:
        for var_name, params in conf_source["numbers"].items():
            min, max, precision = params
            config[var_name] = round(random.uniform(min, max), precision)
    
    if "enums" in conf_source:
        for var_name, options in conf_source["enums"].items():
            config[var_name] = random.choice(options)

    if "choices" in conf_source:
        for options in conf_source["choices"]:
            selection = random.choice(options)
            for o in options:
                config[o] = o == selection
    
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

    if not page_number:
        interval = max(tree_y)
        return interval[1] - interval[0]
    
    tree_y.remove(max(tree_y)) # Cannot optimize the space below the page number
    tree_y.remove(min(tree_y)) # Cannot optimize the space above the highest text block

    return max(i[1]-i[0] for i in tree_y)


def generate(config, filename, temp_path):
    """
    Builds a PDF with the values defined in config
    """
    # ----------------------------------------
    # Names and paths
    # ----------------------------------------
    filename_tex = filename + ".tex"
    filename_pdf = filename + ".pdf"
    tex_path = os.path.join(temp_path, filename_tex)
    pdf_path = os.path.join(temp_path, filename_pdf)

    # Config generation

    # ----------------------------------------
    # PDF generation
    # ----------------------------------------
    write_variables(config, temp_path)

    compile_latex(tex_path)
    # shutil.copyfile(os.path.join(temp_path, filename_pdf), pdf_path)

    row = config.copy()
    row["nbPages"] = page_count(pdf_path)
    row["space"] = get_space(pdf_path)

    return row

def generate_random(conf_source, filename, temp_path):
    """
    Builds a PDF from a random config based on conf_source
    """
    config = random_config(conf_source)
    return generate(config, filename, temp_path)


def decision_tree(csv_path, perc=100, output_path=None):

    # Here we could keep the previous df because it has the same values but we would need to manually set the types (object by default)
    df = dt_al.load_csv(csv_path)
    
    # Replace string values by booleans with one-hot method
    df, features = dt_al.refine_csv(df)
    # Get the training sample size
    sample = dt_al.get_sample_size(df, perc)
    # Separate the data
    train, test, y = dt_al.split_frame(df, features, sample)
    # Create the Decision Tree classifier
    dt = dt_al.create_dt(train, y, sample, min_samples_split = 4)
    
    # Only useful for testing, but we may use 100% of the data for training, and skip the computing of the accuracy
    if perc < 100:
        print("Accuracy :", dt.score(test, y[sample:]))

    # Generate a .dot and a .png file of the tree if there is an output path
    if output_path:
        dt_al.visualize_tree(dt, features, output_path)

    return dt