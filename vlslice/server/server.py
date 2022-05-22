import argparse
import base64
import io
import os

from flask import Flask, send_from_directory

import numpy as np
from PIL import Image

from scipy import stats
from sklearnex import patch_sklearn
patch_sklearn()
import sklearn
from sklearn import cluster

import tables
import torch
from transformers import CLIPProcessor, CLIPModel
import yaml

# CMD ARGUMENTS
default_cfg = f"{os.path.dirname(os.path.abspath(__file__))}/config.yml"
parser = argparse.ArgumentParser()
parser.add_argument("-c", "--config", default=default_cfg, help="YAML VLSlice config")
args = parser.parse_args()

# YAML CONFIG
cfg = yaml.load(open(args.config, 'r'), Loader=yaml.CLoader)
print(cfg)

# FLASK APP CONFIG
app = Flask(__name__)
app.config.from_object(cfg["flask"])

# GLOBAL SESSION INFO
gsession = {
    "data": None
}

@app.before_first_request
def setup():
    gsession["data"] = cfg["data"]["start"]

# Display a random number
@app.route("/rand")
def hello():
    gsession["data"] += 1
    return str(gsession["data"])

# Path for main Svelte page
@app.route("/")
def base():
    return send_from_directory("../client/public", "index.html")

# Static files (compiles JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory("../client/public", path)

if __name__ == "__main__":
    app.run(debug=True)
