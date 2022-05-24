import argparse
import os
import signal
import sys

from sklearnex import patch_sklearn
patch_sklearn()

from flask import Flask, send_from_directory, request
import numpy as np
from scipy import stats
import sklearn
from sklearn import cluster
import tables
import yaml

from model import load_model, clip_sim, delta_c
from utils import img2b64, img2html, cart


# CMD ARGUMENTS
default_cfg = f'{os.path.dirname(os.path.abspath(__file__))}/config.yml'
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', default=default_cfg, help='YAML VLSlice config')
args = parser.parse_args()

# YAML CONFIG
cfg = yaml.load(open(args.config, 'r'), Loader=yaml.CLoader)
print(cfg)

# FLASK APP CONFIG
app = Flask(__name__)
app.config.from_object(cfg['flask'])

# GLOBAL SESSION INFO
gsession = {
    'data': {},
    'model': None
}


# SERVER SETUP / TEARDOWN
@app.before_first_request
def setup():
    # Load data
    h5file = tables.open_file('/nfs/hpc/sw_data/slymane/openimages_64x64.h5')
    filt = ~np.isin(h5file.root.labels, np.char.encode(cfg['data']['exclude_classes']))
    gsession['data'] = {
        'h5file': h5file,
        'imgs': h5file.root.images,
        'imgs_idx': np.where(filt)[0],
        'imgs_emb': h5file.root.clip[:][filt]
    }

    # Load model
    gsession['model'] = load_model(**cfg['model'])


def shutdown(sig=None, frame=None):
    if 'h5file' in gsession['data']:
        gsession['data']['h5file'].close()

    print('Shutting down server...')
    sys.exit(0)
signal.signal(signal.SIGINT, shutdown)  # NOQA: E305


# Display a random number
@app.route('/filter', methods=['POST'])
def filter():
    print(request.json)
    return {'mykey': "hello world!"}


# Path for main Svelte page
@app.route('/')
def base():
    return send_from_directory('../client/public', 'index.html')


# Static files (compiles JS/CSS, etc.)
@app.route('/<path:path>')
def home(path):
    return send_from_directory('../client/public', path)


if __name__ == '__main__':
    app.run(debug=True)
