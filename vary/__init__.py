from flask import Flask
from vary.model.files.directory import create_dir, get_secret_key
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
app.secret_key = get_secret_key(os.path.join("vary", "key"))

# Creates the result folder as an empty folder is not saved by GIT
create_dir(RESULT_FOLDER)

import vary.views
