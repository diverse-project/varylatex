from flask import Flask
import os

# Constants
SERVER_SOURCE_FOLDER = "source"
UPLOAD_FOLDER = os.path.join("vary", SERVER_SOURCE_FOLDER)
SERVER_RESULTS_FOLDER = "results"
RESULT_FOLDER = os.path.join("vary", SERVER_RESULTS_FOLDER)
ALLOWED_EXTENSIONS = {"zip"}

# App
app = Flask(__name__)
# Config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024 * 1024
app.secret_key = "This k3y shouldn't be posted on g1thub"

import vary.views
