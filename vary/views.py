import os
import zipfile
import json

from pathlib import Path

from flask import flash, request, redirect, url_for, render_template, session
from flask import send_from_directory
from werkzeug.utils import secure_filename

import pandas as pd
from pandas.core.common import flatten

from vary import app
from vary.model.files import check_filename, create_temporary_copy, clear_directory
from vary.model.optimizer import generate_random, generate_bbl, decision_tree
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

@app.route('/selectfile')
def selectfile():
    name = session['project_name']
    return render_template('selectfile.html', name=name)

@app.route('/results')
def results():
    name = session['project_name']
    session['main_file_name'] = request.args.get('filename')
    return render_template("results.html", name=name)

@app.route('/compile', methods=["POST"])
def compile():
    generations = 20
    output = "vary/results"
    
    filename = session['main_file_name'].replace(".tex","") # main file file name without extention

    source = os.path.join(app.config['UPLOAD_FOLDER']) # The project is located in the "source" folder

    temp_path = create_temporary_copy(source) # Create the temporary working directory

    generate_bbl(os.path.join(temp_path, filename)) # LaTeX bbl pregeneration

    # Load the variables
    conf_source_path = os.path.join(source, "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    # DataFrame initialisation 
    cols = conf_source["booleans"] + list(conf_source["numbers"].keys()) + list(conf_source["enums"].keys()) + list(flatten(conf_source["choices"])) + ["nbPages", "space", "idConfiguration"]
    df = pd.DataFrame(columns = cols)

    for i in range(generations):
        row = generate_random(conf_source, filename, temp_path)
        row["idConfiguration"] = i
        df = df.append(row, ignore_index = True)
        print(f"Doc {i} generated")

    # Clean working directory
    clear_directory(os.path.dirname(temp_path))


    # Create the output directory
    Path(output).mkdir(parents=True, exist_ok=True)
    # Export results to CSV
    csv_result_path = os.path.join(output,"result.csv")
    df.to_csv(csv_result_path, index=False)
    decision_tree(csv_result_path, output_path=output)

    return send_from_directory("results","result.csv")

@app.route('/tree_img')
def get_tree():
    response = send_from_directory("results",'dt.png')
    response.headers['Cache-Control'] = 'max-age=0, no-cache, must-revalidate'
    return response

@app.route('/filenames')
def get_filenames():
    return json.dumps([x for x in os.listdir("vary/source") if os.path.isfile(os.path.join("vary/source",x))])