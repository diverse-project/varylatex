import os
import subprocess
from vary.model.generation.subcall import run_command


def generate_bbl(filepath):
    """
    Loads the bibliography file
    """
    working_directory, texfile = os.path.split(filepath)
    
    try:
        # Precompile the main file to get the .aux file
        run_command(["pdflatex", "-draftmode", "-interaction=batchmode", texfile + ".tex"], working_directory)
        # Load the bibtex references from the .aux
        run_command(["bibtex", texfile + ".aux"], working_directory)
    except subprocess.TimeoutExpired:
        print("The bibliography compilation process timed out")


def compile_latex(filename):
    """
    Compile the document with pdftex.
    After the generation of the bibliography we may need two runs to link all the references.
    """
    working_directory, texfile = os.path.split(filename)
    try:
        command = ["pdflatex", "-interaction=batchmode", texfile]
        run_command(command, working_directory)
        run_command(command, working_directory)
        return True
    except subprocess.TimeoutExpired:
        return False
