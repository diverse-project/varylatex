import os
import zipfile

from flask import flash, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename

from vary import app
from vary.model.files import check_filename
from vary.model.overleaf_util import fetch_overleaf


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
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        flash('Project uploaded !')

        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(app.config['UPLOAD_FOLDER'])
        os.remove(filepath)
        return redirect(url_for('selectfile'))

@app.route('/import_overleaf', methods=['POST'])
def import_overleaf():
    key = request.form.get('key')
    fetch_overleaf(key, app.config['UPLOAD_FOLDER'])
    return redirect(url_for('selectfile'))
