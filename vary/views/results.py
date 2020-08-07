import os
import json

from flask import session, render_template, send_from_directory, request

from vary import app, RESULT_FOLDER
from vary.model.decision_trees.analysis import eval_options, decision_tree

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
    max_pages = 4

    conf_source_path = os.path.join(app.config["UPLOAD_FOLDER"], "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    csv_path = os.path.join(RESULT_FOLDER, "result.csv")

    classifier, features = decision_tree(csv_path, max_pages)

    probas = eval_options(classifier, config, conf_source, features)
    return json.dumps(probas)
