import os
import re
import shutil
import json
import math
from vary import ALLOWED_EXTENSIONS


def check_filename(filename):
    """
    Checks the name of an uploaded file to make sure it has the right format
    """
    return "." in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def clear_directory(path):
    """
    Removes the content of a directory without removing the directory itself
    """
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))


def create_temporary_copy(path):
    tmp_path = os.path.join(os.getcwd(), "vary/build/latex")
    try:
        shutil.copytree(path, tmp_path)
        macro_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "macros.tex")
        macro_copy_path = os.path.join(tmp_path, "macros.tex")
        shutil.copyfile(macro_path, macro_copy_path)
    except shutil.Error:
        print("Error creating the temporary copy")

    return tmp_path

def inject_space_indicator(filepath):
    filepath_tex = filepath + ".tex"
    to_inject = \
        "\\newwrite\\writeRemSpace\n"+\
        "\\immediate\\openout\\writeRemSpace=space.txt\n"+\
        "\\immediate\\write\\writeRemSpace{\\the\\dimexpr\\pagegoal-\\pagetotal-\\baselineskip\\relax}\n"+\
        "\\immediate\\closeout\\writeRemSpace\n"
    pattern = re.compile(r"^[^%]*\\end{document}")
    with open(filepath_tex, 'r+') as file:
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

def merge_configs(json_config_path, config):
    """
    Adds the variables contained in config to the json config file
    """
    with open(json_config_path) as f:
        conf_source = json.load(f)
        res_conf = _merge_dicts(conf_source, config)
    with open(json_config_path, 'w') as f:
        json.dump(res_conf, f, indent=4)

def _merge_dicts(base_dict, second_dict):
    output_dict = base_dict.copy()
    for key, value in second_dict.items():
        if key in base_dict:
            if type(value) == list:
                output_dict[key] += value
            elif type(value) == dict:
                output_dict[key] = _merge_dicts(output_dict[key], value)
            else:
                output_dict[key] = value
        else:
            output_dict[key] = value
    return output_dict

def float_variable_to_range(variable):
    precision = round(2-math.log10(variable))
    min_val = round(variable*0.7, precision)
    max_val = round(variable*1.3, precision)
    return [min_val, max_val, precision]

def add_graphics_variables(main_file_path):
    (base_path, filename) = os.path.split(main_file_path)
    subfiles = [os.path.join(base_path, name) for name in get_sub_files(main_file_path)]
    subfiles.append(main_file_path)
    variables = {}
    for file_path in subfiles:
        set_values = add_graphics_variables_to_file(file_path)
        variables = _merge_dicts(variables, {k: float_variable_to_range(v) for k, v in set_values.items()})
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
        documentclass_pattern = re.compile(r"\\documentclass{[^}]*}")
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

def init_variables_json(path):
    json_path = os.path.join(path, "variables.json")
    open(json_path, 'a').close()  # Creates the file if it is missing
    with open(json_path, 'r+') as f:
        if not f.read():  # If the file is empty (or has just been created)
            f.write("{}")
    template = {
        "booleans": [],
        "numbers": {},
        "enums": {},
        "choices": []
    }
    merge_configs(json_path, template)
