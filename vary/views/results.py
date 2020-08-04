import os
import json

from flask import session, render_template, send_from_directory, request, g

from vary import app
from vary.model.decision_trees.analysis import eval_options

@app.route('/results')
def results():
    name = session['project_name']
    return render_template("results.html", name=name)


@app.route('/tree_img')
def get_tree():
    response = send_from_directory("results", 'dt.png')
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route("/predict", methods=["POST"])
def predict():
    config = request.form

    conf_source_path = os.path.join(app.config["UPLOAD_FOLDER"], "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    probas = eval_options(app.classifier, config, conf_source, app.features, 4)
    return json.dumps(probas)
