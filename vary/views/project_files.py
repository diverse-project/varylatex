import os
import json
import re

from flask import request, redirect, url_for, render_template, session, send_from_directory

from vary import app

VARIABLE_FILE_NAME = "variables.json"


@app.route('/selectfile', methods=["GET", "POST"])
def selectfile():
    if request.method == "POST":
        session['main_file_name'] = request.form.get('filename')
        return redirect(url_for('mode'))
    else:
        return render_template('selectfile.html')


@app.route('/filenames')
def get_filenames():
    """
    Gets the potential main tex file names based on the content of the source folder and
    the fact that it contains or not a \documentclass{} declaration
    """
    filenames = []
    dc_pattern = re.compile(r"^[^%]*\\begin{document}")
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
