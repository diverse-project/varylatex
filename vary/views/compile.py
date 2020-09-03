import os
import json

from flask import session, send_from_directory, request, g
from shutil import copyfile

from vary import app
from vary.model.generation.compile import generate_bbl
from vary.model.generation.generate import generate_random, generate_pdfs
from vary.model.files.directory import create_temporary_copy, clear_directory
from vary.model.files.tex_injection import inject_space_indicator


@app.route('/compile/<int:generations>', methods=["POST"])
def compile_pdfs(generations, reset=True):
    output = "vary/results"
    filename = session['main_file_name'].replace(".tex", "")  # main file name without extension
    source = app.config['UPLOAD_FOLDER']  # The project is located in the "source" folder
    reset = request.form.get("reset") == 'true'

    generate_pdfs(filename, source, output, generations, reset)
    return send_from_directory("results", "result.csv")


@app.route('/build_pdf', methods=['GET', 'POST'])
def build_pdf():
    filename = session['main_file_name'].replace(".tex", "")
    if request.method == "GET":
        resp = send_from_directory("results", filename + ".pdf")
        resp.headers['Cache-Control'] = 'max-age=0, no-cache, must-revalidate'
        return resp

    config = request.form
    output = "vary/results"
    source = os.path.join(app.config['UPLOAD_FOLDER'])
    temp_path = create_temporary_copy(source)
    file_path = os.path.join(temp_path, filename)

    inject_space_indicator(file_path)
    generate_bbl(file_path)

    conf_source_path = os.path.join(source, "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    generate_random(conf_source, filename, temp_path, config)

    outpath = os.path.join(output, filename + ".pdf")
    if os.path.exists(outpath):
        os.remove(outpath)
    copyfile(
        os.path.join(temp_path, filename + ".pdf"),
        os.path.join(outpath)
    )
    clear_directory(os.path.dirname(temp_path))
    return '{"success":true}', 200, {'ContentType': 'application/json'}
