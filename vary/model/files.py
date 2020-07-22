import os
import re
import shutil
from vary import ALLOWED_EXTENSIONS


def check_filename(filename):
    """
    Checks the name of an uplodaded file to make sure it has the right format
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
    tmp_path = os.path.join(os.path.dirname(path), "build/latex")
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
        file.seek(0) # Go back to the beginning of the file
        file.writelines(lines)

def get_remaining_space(path):
    space_file_path = os.path.join(path, "space.txt")
    with open(space_file_path) as f:
        content = f.read()
        return float(content[:-3])
    return 0.0