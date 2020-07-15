import os
import shutil
import subprocess
import random
import json

import vary.model.decision_trees.analysis as dt_al
from vary.model.generation.inject import write_variables
from vary.model.generation.compile import compile_latex
from vary.model.generation.analyze_pdf import page_count, get_space

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

def generate(config, filename, temp_path):
    """
    Builds a PDF with the values defined in config. The bibliography should already be loaded.
    Returns a dictionnary with the config and the calculated values of the PDF (number of pages, space left).
    """
    filename_tex = filename + ".tex"
    filename_pdf = filename + ".pdf"
    tex_path = os.path.join(temp_path, filename_tex)
    pdf_path = os.path.join(temp_path, filename_pdf)

    write_variables(config, temp_path)

    compile_latex(tex_path)
    
    row = config.copy()
    row["nbPages"] = page_count(pdf_path)
    row["space"] = get_space(pdf_path)

    return row

def generate_random(conf_source, filename, temp_path):
    """
    Builds a PDF from a random config based on conf_source.
    Returns a dictionnary with the config and the calculated values of the PDF (number of pages, space left).
    """
    config = random_config(conf_source)
    return generate(config, filename, temp_path)