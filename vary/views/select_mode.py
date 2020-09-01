from flask import render_template
from vary import app


@app.route("/mode")
def mode():
    return render_template("select_mode.html")
