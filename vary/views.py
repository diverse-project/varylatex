import os
import zipfile
import json

from pathlib import Path
import re

from flask import flash, request, redirect, url_for, render_template, session
from flask import send_from_directory
from werkzeug.utils import secure_filename

from shutil import copyfile

import pandas as pd
from pandas.core.common import flatten

from vary import app
from vary.model.files import check_filename, create_temporary_copy, clear_directory
from vary.model.generation.generate import generate_random, generate_pdf
from vary.model.generation.compile import generate_bbl
from vary.model.decision_trees.analysis import decision_tree
from vary.model.overleaf_util import fetch_overleaf


@app.route('/', methods=["GET","POST"])
def index():
    
    if request.method == "POST":
        if 'file' not in request.files:
            flash('No file part in the request')
            return redirect(request.url)
        file = request.files['file']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if check_filename(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            flash('Project uploaded !')

            with zipfile.ZipFile(filepath,"r") as zip_ref:
                zip_ref.extractall(app.config['UPLOAD_FOLDER'])
            os.remove(filepath)
            session['project_name'] = file.filename.rsplit(".")[0]
            return redirect(url_for('selectfile'))
        else:
            flash('File not valid, please upload a zip file of the project')
            return redirect(request.url)
    else:
        return render_template('index.html')


@app.route('/import_overleaf', methods=['POST'])
def import_overleaf():
    key = request.form.get('key')
    fetch_overleaf(key, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('selectfile'))


@app.route('/selectfile', methods = ["GET", "POST"])
def selectfile():
    if request.method == "POST":
        session['main_file_name'] = request.form.get('filename')
        return redirect(url_for('results'))
    else:
        name = session['project_name']
        return render_template('selectfile.html', name=name)


@app.route('/results')
def results():
    name = session['project_name']
    return render_template("results.html", name=name)


@app.route('/compile/<int:generations>', methods=["POST"])
@app.route('/compile/<int:generations>/<reset>', methods=["POST"])
def compile(generations, reset=True):
    output = "vary/results"
    
    filename = session['main_file_name'].replace(".tex", "")  # main file file name without extension

    source = os.path.join(app.config['UPLOAD_FOLDER'])  # The project is located in the "source" folder

    temp_path = create_temporary_copy(source)  # Create the temporary working directory

    generate_bbl(os.path.join(temp_path, filename))  # LaTeX bbl pregeneration
    
    # Load the variables
    conf_source_path = os.path.join(source, "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    # DataFrame initialisation
    csv_result_path = os.path.join(output, "result.csv")

    if reset == True:
        cols = conf_source["booleans"]\
               + list(conf_source["numbers"].keys())\
               + list(conf_source["enums"].keys())\
               + list(flatten(conf_source["choices"]))\
               + ["nbPages", "space"]
        df = pd.DataFrame(columns=cols)
    else:
        df = pd.read_csv(csv_result_path, index_col=0)

    for i in range(generations):
        row = generate_random(conf_source, filename, temp_path)
        df = df.append(row, ignore_index=True)

    # Clean working directory
    clear_directory(os.path.dirname(temp_path))

    # Create the output directory
    Path(output).mkdir(parents=True, exist_ok=True)
    # Export results to CSV
    df.to_csv(csv_result_path)
    decision_tree(csv_result_path, output_path=output)

    return send_from_directory("results","result.csv")


@app.route('/build_pdf', methods=['GET','POST'])
def build_pdf():
    filename = session['main_file_name'].replace(".tex","")
    if request.method == "GET":
        resp = send_from_directory("results", filename + ".pdf")
        resp.headers['Cache-Control'] = 'max-age=0, no-cache, must-revalidate'
        return resp

    config = request.form
    output = "vary/results"
    source = os.path.join(app.config['UPLOAD_FOLDER'])
    temp_path = create_temporary_copy(source)
    generate_bbl(os.path.join(temp_path, filename))

    generate_pdf(config, filename, temp_path)
    
    outpath = os.path.join(output, filename + ".pdf") 
    if os.path.exists(outpath):
        os.remove(outpath)
    copyfile(
        os.path.join(temp_path, filename + ".pdf"),
        os.path.join(outpath)
    )
    print(config)
    return '{"success":true}', 200, {'ContentType': 'application/json'}


@app.route('/tree_img')
def get_tree():
    response = send_from_directory("results",'dt.png')
    response.headers['Cache-Control'] = 'no-store'
    return response


@app.route('/filenames')
def get_filenames():
    """
    Gets the potential main tex file names based on the content of the source folder and
    the fact that it contains or not a \documentclass{} declaration
    """
    filenames = []
    dc_pattern = re.compile(r"^[^%]*\\documentclass\{[^}]*\}")
    texfile_pattern = re.compile(r".*\.tex")
    for root, _, files in os.walk("vary/source"):
        for filename in files:
            if texfile_pattern.match(filename):
                path = os.path.join(root, filename)
                with open(path) as file:
                    data = file.read()
                    if any(l for l in data.splitlines() if dc_pattern.match(l)):
                        filenames.append(os.path.relpath(path, "vary/source"))

    return json.dumps(filenames)