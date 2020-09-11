import os
import json
import re

from flask import request, redirect, url_for, render_template, session, send_from_directory

from vary import app
from vary.model.files.tex_injection import add_graphics_variables, add_include_macros_variables, add_itemsep_variable

VARIABLE_FILE_NAME = "variables.json"


@app.route('/selectfile', methods=["GET", "POST"])
def selectfile():
    if request.method == "POST":
        main_filename = request.form.get('filename')
        session['main_file_name'] = main_filename
        upload_folder = app.config['UPLOAD_FOLDER']
        add_include_macros_variables(os.path.join(upload_folder, main_filename))
        return redirect(url_for('auto_variables'))
    else:
        return render_template('selectfile.html')


@app.route('/filenames')
def get_filenames():
    """
    Gets the potential main tex file names based on the content of the source folder and
    the fact that it contains or not a \documentclass{} declaration
    """
    filenames = []
    dc_pattern = re.compile(r"\\documentclass(\[[^\]]*\])*{[^}]*}")
    texfile_pattern = re.compile(r".*\.tex")
    for root, _, files in os.walk(app.config['UPLOAD_FOLDER']):
        for filename in files:
            if texfile_pattern.match(filename):
                path = os.path.join(root, filename)
                with open(path) as file:
                    data = file.read()
                    if any(li for li in data.splitlines() if dc_pattern.match(li)):
                        filenames.append(os.path.relpath(path, "vary/source"))

    return json.dumps(filenames)


@app.route('/config_src')
def config_src():
    """
    Gets the config JSON file of the project, which defines the domain of the variables.
    """
    return send_from_directory("source", VARIABLE_FILE_NAME)


@app.route('/auto_variables', methods=["GET", "POST"])
def auto_variables():
    if request.method == "POST":
        project_folder = app.config['UPLOAD_FOLDER']
        main_file_path = os.path.join(project_folder, session['main_file_name'])
        form = request.form
        if form.get('generateImageSizes'):
            add_graphics_variables(main_file_path)
        if form.get("generateItemsep"):
            add_itemsep_variable(main_file_path)

        return redirect(url_for('mode'))

    else:
        return render_template("auto_variables.html")
