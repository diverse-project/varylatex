import os
import json

from flask import session, render_template, send_from_directory, request

from vary import app, RESULT_FOLDER
from vary.model.decision_trees.analysis import eval_options, decision_tree

@app.route('/constraints')
def constraints():
    return render_template("constraints.html")


@app.route('/tree_img')
def get_tree():
    response = send_from_directory("results", 'dt.png')
    response.headers['Cache-Control'] = 'no-store'
    return response

@app.route("/predict/<int:max_pages>", methods=["POST"])
def predict(max_pages):
    config = request.json
    conf_source_path = os.path.join(app.config["UPLOAD_FOLDER"], "variables.json")
    with open(conf_source_path) as f:
        conf_source = json.load(f)

    csv_path = os.path.join(RESULT_FOLDER, "result.csv")

    classifier, features = decision_tree(csv_path, max_pages)

    probas = eval_options(classifier, config, conf_source, features)
    return json.dumps(probas)
