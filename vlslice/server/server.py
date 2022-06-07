import argparse
import os
import signal
import sys
from sklearnex import patch_sklearn
patch_sklearn()

from flask import Flask, g, request, send_from_directory, jsonify
import numpy as np
import pandas as pd
from scipy import stats
import sklearn
from sklearn import cluster
import tables
import yaml

from model import load_model, clip_sim, delta_c
from utils import img2b64, cart


# CMD ARGUMENTS
default_cfg = f'{os.path.dirname(os.path.abspath(__file__))}/config.yml'
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--config', default=default_cfg, help='YAML VLSlice config')
args = parser.parse_args()

# YAML CONFIG
cfg = yaml.load(open(args.config, 'r'), Loader=yaml.CLoader)

# FLASK APP CONFIG
app = Flask(__name__)
app.config.from_object(cfg['flask'])

# SERVER CONTEXT
gserv = {
    'data': {},
    'model': None
}


# SERVER SETUP / TEARDOWN
@app.before_first_request
def setup():
    # Load data
    h5file = tables.open_file('/nfs/hpc/sw_data/slymane/openimages_64x64.h5')
    filt = ~np.isin(h5file.root.labels, np.char.encode(cfg['data']['exclude_classes']))
    gserv['data'] = {
        'h5file': h5file,
        'imgs': h5file.root.images,
        'imgs_idx': np.where(filt)[0],
        'imgs_emb': h5file.root.clip[:][filt]
    }

    # Load model
    gserv['model'] = load_model(**cfg['model'])


def shutdown(sig=None, frame=None):
    if 'h5file' in gserv['data']:
        gserv['data']['h5file'].close()

    print('Shutting down server...')
    sys.exit(0)
signal.signal(signal.SIGINT, shutdown)  # NOQA: E305


# Display a random number
@app.route('/filter', methods=['POST'])
def filter():
    # Parse request
    baseline = request.json['baseline']  # Basleline text caption
    augment = request.json['augment']    # Augmented text caption
    k = request.json['k']                # Topk results to filter
    w = request.json['w']                # Distance/DC cluster weight
    dt = request.json['dt']              # Clustering distance threshold

    # Embed text captions
    txt_embs = gserv['model'](txt=[baseline, augment])
    sims = clip_sim(txt_embs, gserv['data']['imgs_emb'])

    # Filter data by captions
    g.topk = np.argsort(sims[:, 0])[-k:]
    g.topkidxs = gserv['data']['imgs_idx'][g.topk]
    g.topkembs = gserv['data']['imgs_emb'][g.topk]
    g.topksims = sims[g.topk]
    g.topkdc = delta_c(g.topksims)

    # Get distances
    dist_embs = (1 - np.matmul(g.topkembs, g.topkembs.transpose())).clip(0.0, 1.0)
    dist_dc = sklearn.metrics.pairwise.euclidean_distances((g.topkdc.reshape(-1, 1) + 1) / 2)
    dist = w * dist_embs + (1 - w) * dist_dc

    # Cluster
    clusterer = cluster.AgglomerativeClustering(
        n_clusters=None,
        affinity='precomputed',
        linkage='average',
        distance_threshold=dt,
        memory='cache/'
    ).fit(dist)
    clusters = np.char.mod('%i', clusterer.labels_).astype('U128')

    # Build dataframe for cluster-level dc metrics
    pd_data = []
    json_data = []
    for c in np.unique(clusters):
        dc = g.topkdc[clusters == c]
        c_mean = dc.mean()
        c_var = dc.var().clip(min=0.0)

        pd_data.append([c, c_mean, c_var, len(dc)])

        json_data.append({
            'id': c.item(),
            'mean': c_mean.item(),
            'variance': c_var.item(),
            'size': len(dc),
            'images': [{
                'id': i.item(),
                'b64': img2b64(i, gserv['data']['imgs']),
                'selected': False
            } for i in g.topkidxs[clusters == c]]
        })

    g.df = pd.DataFrame(pd_data, columns=['id', 'mean', 'var', 'size'])
    return jsonify(json_data)


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
