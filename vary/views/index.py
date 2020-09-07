import os
import zipfile

from flask import flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

from vary import app, ALLOWED_EXTENSIONS
from vary.model.overleaf_util import fetch_overleaf
from vary.model.files.directory import clear_directory
from vary.model.files.dictionnaries import init_variables_json

@app.route('/', methods=["GET", "POST"])
def index():
    """
    First page, which gives a choice between two methods for selecting a project.
    """
    return render_template('index.html')

@app.route('/upload_project', methods=['POST'])
def upload_project():
    if 'file' not in request.files:
        flash('No file part in the request')
        return redirect(request.url)
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if check_filename(file.filename):
        upload_folder = app.config['UPLOAD_FOLDER']
        clear_directory(upload_folder)  # Delete potential previous project

        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        flash('Project uploaded !')

        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(upload_folder)
        os.remove(filepath)
        init_variables_json(upload_folder)
        return redirect(url_for('selectfile'))

@app.route('/import_overleaf', methods=['POST'])
def import_overleaf():
    key = request.form.get('key')
    fetch_overleaf(key, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('selectfile'))

def check_filename(filename):
    """
    Checks the name of an uploaded file to make sure it has the right format
    """
    return "." in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS