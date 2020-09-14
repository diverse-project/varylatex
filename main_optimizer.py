import argparse
import os
import json
import shutil

import pandas as pd
from pandas.core.common import flatten

from vary.model.overleaf_util import fetch_overleaf
from vary.model.files.directory import clear_directory, create_temporary_copy, create_dir
from vary.model.files.tex_injection import inject_space_indicator
from vary.model.generation.generate import generate_random, generate_pdf
from vary.model.generation.compile import generate_bbl
from vary.model.decision_trees.analysis import decision_tree

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", help="Name of the file you want to compile")
    parser.add_argument("-s", "--source", default=os.path.join(os.getcwd(),"vary/source"),
                        help="Path of the LaTeX source folder")
    parser.add_argument("-v", "--verbose", action="store_true", help="Notifies when a PDF is generated")
    parser.add_argument("-o", "--output", default=os.path.join(os.getcwd(), "vary/results"),
                        help="The path of the output folder")
    parser.add_argument("-g", "--generations", default=10, type=int,
                        help="Amount of randomly generated configs used to generate the tree")
    parser.add_argument("-ts", "--trainsize", default=100, type=int,
                        help="Percentage of the generations used to train the tree (the rest is used to calculate the \
                        accuracy)")
    parser.add_argument("-ol", "--overleaf",
                        help="Key of the readonly link of the project on Overleaf (the letters avter '/read/'). \
                        It needs to have a 'values.json' file and the document must include 'macros' and 'values'")
    parser.add_argument("-c", "--config", help="Generate a specific PDF from a config JSON string")
    parser.add_argument("-p", "--maxpages", type=int, help="The maximum amount of pages accepted for the document")
    args = parser.parse_args()

    document_path = args.source
    filename = args.filename.replace(".tex","")

    if args.overleaf:
        clear_directory(document_path)
        fetch_overleaf(args.overleaf, document_path)

    temp_path = create_temporary_copy(document_path)

    conf_source_path = os.path.join(document_path, "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    # DataFrame initialisation 
    cols = conf_source["booleans"] + \
        list(conf_source["numbers"].keys()) + \
        list(conf_source["enums"].keys()) + \
        list(flatten(conf_source["choices"])) + \
        ["nbPages", "space"]
    df = pd.DataFrame(columns=cols)

    file_path = os.path.join(temp_path, filename)
    inject_space_indicator(file_path)
    # LaTeX bbl pregeneration
    generate_bbl(file_path)

    # ----------------------------------------
    # PDF generation
    # ----------------------------------------
    if args.config:
        row = generate_pdf(json.loads(args.config), filename, temp_path)
        pdf_name = filename+".pdf"
        shutil.copyfile(os.path.join(temp_path, pdf_name), os.path.join(args.output, pdf_name))
    else:
        for i in range(args.generations):
            row = generate_random(conf_source, filename, temp_path)
            df = df.append(row, ignore_index=True)
            if args.verbose:
                print(f"Doc {i} generated")

    # Clean working directory
    shutil.rmtree(temp_path)
    # Create the output directory
    create_dir(args.output)
    # Export results to CSV
    result_path = os.path.join(args.output, "result.csv")
    df.to_csv(result_path)

    # ----------------------------------------
    # Decision Tree Analysis
    # ----------------------------------------
    if args.config:
        exit()  # Not useful for single generation
    # Percentage of the sample used to create the tree
    # When using the tool we could use 100% of the data as we want the tree to be as precise as possible
    perc = args.trainsize

    if args.maxpages:
        decision_tree(result_path, args.maxpages, perc, args.output)
