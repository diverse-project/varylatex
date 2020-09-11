import os
import re
import math

from vary.model.files.dictionnaries import merge_dicts, merge_configs

def inject_space_indicator(file_path):
    """
    Adds a command to the main .tex file to write the remaining space on the PDF at the end of the document.
    The result of the LaTeX command is an output in a file called "space.txt" with the space left.
    The "space.txt" file is created during the PDF generation.
    """
    file_path_tex = file_path + ".tex"
    to_inject = \
        "\\newwrite\\writeRemSpace\n"+\
        "\\immediate\\openout\\writeRemSpace=space.txt\n"+\
        "\\immediate\\write\\writeRemSpace{\\the\\dimexpr\\pagegoal-\\pagetotal-\\baselineskip\\relax}\n"+\
        "\\immediate\\closeout\\writeRemSpace\n"
    pattern = re.compile(r"^[^%]*\\end{document}")
    with open(file_path_tex, 'r+') as file:
        lines = file.readlines()
        doc_end_line = 0
        for line in reversed(lines):
            doc_end_line -= 1
            if pattern.match(line):
                break
        lines.insert(doc_end_line, to_inject)
        file.seek(0)  # Go back to the beginning of the file
        file.writelines(lines)


def get_remaining_space(path):
    """
    Retrieves the remaining space calculated during the PDF build by the space indicator command.
    It does it by reading the "space.txt" log file where it was written.
    """
    space_file_path = os.path.join(path, "space.txt")
    with open(space_file_path) as f:
        content = f.read()
        return float(content[:-3])


def get_sub_files(main_file_path):
    """
    Gets the list of the tex files included in the document
    """
    pattern = re.compile(r"^[^%]*\\(?:input|include)\{([^}]*)}")  # the "in" prefix is not excluded for readability
    sub_files = []
    with open(main_file_path, 'r') as f:
        for line in f.readlines():
            match = pattern.match(line)
            if match:
                sub_files.append(match.group(1))
    return sub_files


def add_graphics_variables_to_file(file_path):
    """
    Looks for all the 'includegraphics' commands in the file and extracts a variation point on the height/width/size.
    Returns a dictionary with the name of the variables as the keys and their initial values as the values.
    """
    dir_path, filename = os.path.split(file_path)
    if not filename.endswith(".tex"):
        filename += ".tex"
        file_path = os.path.join(dir_path, filename)

    if not os.path.isfile(file_path):
        return {}
    

    graphics_pattern = re.compile(r"^[^%]*(\\includegraphics\[([^\]]*)\]\{([^}]*)}).*")
    param_pattern = re.compile(r"(\w+)\s*=\s*([\d.]+)(.*)")
    variables = {}
    with open(file_path, "r+") as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            match = graphics_pattern.match(line)
            if match:
                param = match.group(2)
                graphics_filename = match.group(3)
                param_match = param_pattern.match(param)
                if param_match:
                    param_name = param_match.group(1)
                    param_default_val = param_match.group(2)
                    param_unit = param_match.group(3)
                    var_name = param_name+"_"+graphics_filename
                    variables[var_name] = float(param_default_val)
                    newline = line.replace(
                        match.group(1),
                        fr"\includegraphics[{param_name}=\getVal{{{var_name}}}{param_unit}]{{{graphics_filename}}}"
                    )
                    lines[i] = newline
        f.seek(0)
        f.writelines(lines)
    return variables


def float_variable_to_range(variable):
    """
    Creates a range of values based on a central float value.
    The result is an array with the minimum being 70% of the original value and the maximum being 130%.
    The last element of the array is the digit precision, so the step is around
    one 100th of the magnitude of the original value
    """
    precision = round(2-math.log10(variable))
    min_val = round(variable*0.7, precision)
    max_val = round(variable*1.3, precision)
    return [min_val, max_val, precision]


def add_graphics_variables(main_file_path):
    base_path = os.path.dirname(main_file_path)
    subfiles = [os.path.join(base_path, name) for name in get_sub_files(main_file_path)]
    subfiles.append(main_file_path)
    variables = {}
    for file_path in subfiles:
        set_values = add_graphics_variables_to_file(file_path)
        variables = merge_dicts(variables, {k: float_variable_to_range(v) for k, v in set_values.items()})
    config_path = os.path.join(base_path, "variables.json")
    merge_configs(config_path, {"numbers": variables})


def add_include_macros_variables(main_file_path):
    to_inject = ""
    with open(main_file_path) as f:
        content = f.read()
        try:
            content.index(r"\include{macros}")
        except ValueError:
            to_inject += "\\include{macros}\n"
        try:
            content.index(r"\include{values}")
        except ValueError:
            to_inject += "\\include{values}\n"

    if to_inject:
        documentclass_pattern = re.compile(r"\\documentclass(\[[^\]]*\])*{[^}]*}")
        with open(main_file_path, "r+") as f:
            lines = f.readlines()
            for index, line in enumerate(lines):
                match = documentclass_pattern.search(line)
                if match:
                    break
            if match:
                lines.insert(index + 1, to_inject)
            f.seek(0)
            f.writelines(lines)

def add_itemsep_variable(main_file_path):
    include_values_pattern = re.compile(r"\\include{values}")
    with open(main_file_path, "r+") as f:
        lines = f.readlines()
        for index, line in enumerate(lines):
            match = include_values_pattern.search(line)
            if match:
                break
        if match:
            lines.insert(index + 1, r"\setlength\itemsep{\getVal{itemsep}pt}")
        f.seek(0)
        f.writelines(lines)
    itemsep_dict = {"numbers": {"itemsep": [-5, 5, 1]}}
    base_path = os.path.dirname(main_file_path)
    config_path = os.path.join(base_path, "variables.json")
    merge_configs(config_path, itemsep_dict)
