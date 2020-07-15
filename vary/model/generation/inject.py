import os

def get_variable_def(k, v):
    """
    \\defVal{name}{value}
    """
    if v == False or v == "False":
        return ""
    if v == True:
        return fr"\defVal{{{k}}}{{}}"
    return fr"\defVal{{{k}}}{{{v}}}"


def write_variables(config, temp_path):
    """ Write variables to file """

    with open(os.path.join(temp_path, "values.tex"), "w") as f:
        for k, v in config.items():
            macro = get_variable_def(k, v)
            if macro != "":
                f.write(f"{macro}\n")