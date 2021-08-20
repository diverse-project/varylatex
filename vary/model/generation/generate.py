import os
import random
import json

import pandas as pd

from pandas.core.common import flatten
from pathlib import Path

from vary.model.files.directory import create_temporary_copy, remove_directory
from vary.model.files.tex_injection import inject_space_indicator, get_remaining_space
from vary.model.generation.compile import generate_bbl
from vary.model.generation.inject import write_variables
from vary.model.generation.compile import compile_latex
from vary.model.generation.analyze_pdf import page_count

def random_config(conf_source, fixed_values={}):
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
            config[boolean] = fixed_values[boolean] if boolean in fixed_values else random.choice([True, False])

    if "numbers" in conf_source:
        for var_name, params in conf_source["numbers"].items():
            if var_name in fixed_values:
                config[var_name] = fixed_values[var_name]
            else:
                min_bound, max_bound, precision = params
                config[var_name] = round(random.uniform(min_bound, max_bound), precision)

    if "enums" in conf_source:
        for var_name, options in conf_source["enums"].items():
            config[var_name] = fixed_values[var_name] if var_name in fixed_values else random.choice(options)

    if "choices" in conf_source:
        for options in conf_source["choices"]:
            selection = random.choice(options)
            for o in options:
                if o in fixed_values and fixed_values[o]:
                    selection = o
            for o in options:
                config[o] = o == selection
    
    return config


def generate_pdf(config, filename, temp_path):
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
    row["space"] = get_remaining_space(temp_path)

    return row


def generate_random(conf_source, filename, temp_path, fixes_values={}):
    """
    Builds a PDF from a random config based on conf_source.
    Returns a dictionary with the config and the calculated values of the PDF (number of pages, space left).
    """
    config = random_config(conf_source, fixes_values)
    return generate_pdf(config, filename, temp_path)
    
def generate_pdfs(filename, source, output, nb_gens, reset=True, fixed_values = {}):
    """
    Creates as many PDFs as specified with nb_gens, from a random config based on conf_source, and calculate
    their values. The config and values are stored in a "result.csv" file in the output directory.
    If reset is set to False and there is already a result file, the results are appended to the previous ones.
    """
    temp_path = create_temporary_copy(source)  # Create the temporary working directory
    file_path = os.path.join(temp_path, filename)
    inject_space_indicator(file_path)
    generate_bbl(file_path)  # LaTeX bbl pregeneration

    # Load the variables
    conf_source_path = os.path.join(source, "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    # DataFrame initialisation
    csv_result_path = os.path.join(output, "result.csv")
    df = _create_df(conf_source) if reset else pd.read_csv(csv_result_path, index_col=0)

    for _ in range(nb_gens):
        row = generate_random(conf_source, filename, temp_path, fixed_values)
        df = df.append(row, ignore_index=True)

    # Clean working directory
    remove_directory(temp_path)
    # Create the output directory
    Path(output).mkdir(parents=True, exist_ok=True)
    # Export results to CSV
    df.to_csv(csv_result_path)


def _create_df(conf_source):
    cols = conf_source["booleans"] \
           + list(conf_source["numbers"].keys()) \
           + list(conf_source["enums"].keys()) \
           + list(flatten(conf_source["choices"])) \
           + ["nbPages", "space"]
    return pd.DataFrame(columns=cols)
