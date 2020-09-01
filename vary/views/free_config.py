from flask import render_template
from vary import app

@app.route('/config')
def config():
    return render_template("free_config.html")