import argparse
import os
import signal
import sys
import secrets

from sklearnex import patch_sklearn
patch_sklearn()

from flask import Flask, request, send_from_directory, jsonify, session
from flask_session import Session
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
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = 'filesystem'
app.secret_key = secrets.token_urlsafe(16)
Session(app)

# SERVER CONTEXT
gserv = {
    'data': {},
    'model': None
}

# CLIENT CONTEXT
# session['topk']
# session['topkidxs']
# session['topkembs']
# session['topksims']
# session['topkdc']
# session['clusters']
# session['df']
# session['dist']


# SERVER SETUP / TEARDOWN
@app.before_first_request
def setup():
    # Load data
    h5file = tables.open_file('/nfs/hpc/sw_data/slymane/openimages_b16_2.h5')
    if cfg['dev']:
        print("WARNING: Running in development mode.")
        filt = ~np.isin(h5file.root.labels[:1_000_000], np.char.encode(cfg['data']['exclude_classes']))
        img_embs = h5file.root.clip[:1_000_000][filt]
    else:
        filt = ~np.isin(h5file.root.labels, np.char.encode(cfg['data']['exclude_classes']))
        img_embs = h5file.root.clip[:][filt]

    gserv['data'] = {
        'h5file': h5file,
        'imgs': h5file.root.images,
        'imgs_idx': np.where(filt)[0],
        'imgs_emb': img_embs
    }

    # Load model
    gserv['model'] = load_model(**cfg['model'])


def shutdown(sig=None, frame=None):
    if 'h5file' in gserv['data']:
        gserv['data']['h5file'].close()

    print('Shutting down server...')
    sys.exit(0)
signal.signal(signal.SIGINT, shutdown)  # NOQA: E305


# Filter to working set
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
    session['topk'] = np.argsort(sims[:, 0])[-k:]
    session['topkidxs'] = gserv['data']['imgs_idx'][session['topk']]
    session['topkembs'] = gserv['data']['imgs_emb'][session['topk']]
    session['topksims'] = sims[session['topk']]
    session['topkdc'] = delta_c(session['topksims'])

    # Get distances
    dist_embs = (1 - np.matmul(session['topkembs'], session['topkembs'].transpose())).clip(0.0, 1.0)
    dist_dc = sklearn.metrics.pairwise.euclidean_distances((session['topkdc'].reshape(-1, 1) + 1) / 2)
    session['dist'] = w * dist_embs + (1 - w) * dist_dc

    # Cluster
    clusterer = cluster.AgglomerativeClustering(
        n_clusters=None,
        affinity='precomputed',
        linkage='average',
        distance_threshold=dt,
        memory='cache/'
    ).fit(session['dist'])
    session['clusters'] = np.char.mod('%i', clusterer.labels_).astype('U128')

    # Build dataframe for cluster-level dc metrics
    pd_data = []
    json_data = []
    for c in np.unique(session['clusters']):
        dc = session['topkdc'][session['clusters'] == c]
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
            } for i in session['topkidxs'][session['clusters'] == c]]
        })

    session['df'] = pd.DataFrame(pd_data, columns=['id', 'mean', 'var', 'size'])
    return jsonify(json_data)


# Get similar datapoints
@app.route('/similar', methods=['POST'])
def similar():
    cluster = request.json['cluster']
    c1 = cluster['id']

    # Show related points to explore
    unique, counts = np.unique(session['clusters'], return_counts=True)

    intra_cluster_dist = {c2: 0.0 for c2 in unique}
    cidx1 = np.where(session['clusters'] == c1)[0]
    for c2 in unique:
        cidx2 = np.where(session['clusters'] == c2)[0]
        ca = cart([cidx1, cidx2])
        intra_cluster_dist[c2] = session['dist'][ca[0], ca[1]].mean()

    # Get top10 excluding the selected cluster
    neighbors = sorted(intra_cluster_dist, key=intra_cluster_dist.get)[1:11]

    json_data = {
        "neighbors": neighbors
    }

    return jsonify(json_data)


# Get counterfactual datapoints
@app.route('/counter', methods=['POST'])
def counter():
    cluster = request.json['cluster']
    c1 = cluster['id']

    # Show related points to explore
    unique, counts = np.unique(session['clusters'], return_counts=True)

    intra_cluster_dist = {c2: 0.0 for c2 in unique}
    cidx1 = np.where(session['clusters'] == c1)[0]
    for c2 in unique:
        cidx2 = np.where(session['clusters'] == c2)[0]
        ca = cart([cidx1, cidx2])
        intra_cluster_dist[c2] = session['dist'][ca[0], ca[1]].mean()

    # Get top10 excluding the selected cluster
    if np.sign(cluster['mean']) == -1:
        for key in session['df'][session['df']['mean'] < 0].id:
            intra_cluster_dist.pop(key)
    else:
        for key in session['df'][session['df']['mean'] > 0].id:
            intra_cluster_dist.pop(key)

    counters = sorted(intra_cluster_dist, key=intra_cluster_dist.get)[:10]

    json_data = {
        "counters": counters
    }

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
    app.run(host=cfg['flask']['host'], port=5000, debug=True)
