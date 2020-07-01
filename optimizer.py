import os
import shutil
from distutils.dir_util import copy_tree
import subprocess
import random
import json

from pathlib import Path

import fitz
from intervaltree import Interval, IntervalTree
import pandas as pd
from pandas.core.common import flatten

import argparse


import decision_trees.analysis as dt_al
import overleaf_util as over

def create_temporary_copy(path):
    tmp_path = os.path.join(os.getcwd(), "build")
    #Path(tmp_path).mkdir(parents=True, exist_ok=True)
    try:
        copy_tree(path, tmp_path)
        macro_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "macros.tex")
        macro_copy_path = os.path.join(tmp_path, "macros.tex")
        shutil.copyfile(macro_path, macro_copy_path)
    except:
        print("Error creating the temporary copy")

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


def generate(conf_source, filename, temp_path):

    # ----------------------------------------
    # Names and paths
    # ----------------------------------------
    filename_tex = filename + ".tex"
    filename_pdf = filename + ".pdf"
    tex_path = os.path.join(temp_path, filename_tex)
    pdf_path = os.path.join(temp_path, filename_pdf)

    # Config generation
    config = random_config(conf_source)
    # Uncomment for fixed config
    # config = {'PL_FOOTNOTE': True, 'ACK': False, 'PARAGRAPH_ACK': False, 'LONG_AFFILIATION': True, 'EMAIL': False, 'BOLD_ACK': True, 'LONG_ACK': False, 'vspace_bib': 4.77, 'bref_size': 1.0, 'cserver_size': 0.63, 'js_style': '\\scriptsize'}

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

def clear_directory(path):
    """
    Removes the content of a directory without removing the directory itself
    """
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Name of the file you want to compile")
    parser.add_argument("-s", "--source", default=os.path.join(os.getcwd(),"source"), help="Path of the LaTeX source folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Notifies when a PDF is generated")
    parser.add_argument("-o", "--output", default=os.path.join(os.getcwd(), "output"), help = "The path of the output folder")
    parser.add_argument("-g", "--generations", default=10, type=int, help="Amount of randomly generated configs used to generate the tree")
    parser.add_argument("-ts", "--trainsize", default=100, type=int, help="Percentage of the generations used to train the tree (the rest is used to calculate the accuracy)")
    parser.add_argument("-ol", "--overleaf", help="Key of the readonly link of the project on Overleaf (the letters avter '/read/'). It needs to have a 'values.json' file and the document must include 'macros' and 'values'")
    args = parser.parse_args()

    document_path = args.source
    filename = args.filename.replace(".tex","")

    if (args.overleaf):
        clear_directory(document_path)
        over.fetch_overleaf(args.overleaf, document_path)

    temp_path = create_temporary_copy(document_path)


    # ----------------------------------------
    # Variables
    # ----------------------------------------
    conf_source_path = os.path.join(document_path, "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    # DataFrame initialisation 
    cols = conf_source["booleans"] + list(conf_source["numbers"].keys()) + list(conf_source["enums"].keys()) + list(flatten(conf_source["choices"])) + ["nbPages", "space", "idConfiguration"]
    df = pd.DataFrame(columns = cols)

    # LaTeX bbl pregeneration
    generate_bbl(os.path.join(temp_path, filename))

    # ----------------------------------------
    # PDF generation
    # ----------------------------------------
    for i in range(args.generations):
        row = generate(conf_source, filename, temp_path)
        row["idConfiguration"] = i
        df = df.append(row, ignore_index = True)
        if args.verbose:
            print(f"Doc {i} generated")

        
    # Clean working directory
    clear_directory(temp_path)
    # Create the output directory
    Path(args.output).mkdir(parents=True, exist_ok=True)
    # Export results to CSV
    result_path = os.path.join(args.output,"result.csv")
    df.to_csv(result_path, index=False)

    # ----------------------------------------
    # Decision Tree Analysis
    # ----------------------------------------

    # Percentage of the sample used to create the tree
    # When using the tool we could use 100% of the data as we want the tree to be as precise as possible
    perc = args.trainsize

    # Here we could keep the previous df because it has the same values but we would need to manually set the types (object by default)
    df = dt_al.load_csv(result_path)
    
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

    # Generate a .dot and a .png file of the tree
    dt_al.visualize_tree(dt, features, args.output)


    