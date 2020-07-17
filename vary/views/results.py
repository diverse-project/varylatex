from flask import session, render_template, send_from_directory

from vary import app

@app.route('/results')
def results():
    name = session['project_name']
    return render_template("results.html", name=name)


@app.route('/tree_img')
def get_tree():
    response = send_from_directory("results", 'dt.png')
    response.headers['Cache-Control'] = 'no-store'
    return response
