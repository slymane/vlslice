# VLSlice

## Getting Started

The VLSlice client is built with a JS/Svelte client running on a Python/Flask backend. To run the server, however, only the python dependencies must be installed. The following code blocks walks through downloading precomputed image embeddings from CLIP on OpenImages, creating an appropriate Python environment with conda, and starting the VLSlice server.

There are two options for download data. The "dev" embeddings contain the first million examples, and are much smaller. Those with slow internet or less than 16GB of RAM should consider this version. The "all" embeddings use all 8-million examples and requires >16GB RAM to load. To change between "dev" and "all" embeddings, modify the values of "dev" in [vlslice/server/config.yml](./vlslice/server/config.yml) to `False.`

```bash
# 1. Download Data

# ~2GB, loads into RAM quickly.
# Labels are used for pre-filtering OpenImages as described in Section 4.1.
wget https://d30mxw38m32j53.cloudfront.net/embeddings/embs_dev.npy -O vlslice/server/data/embs_dev.npy
wget https://d30mxw38m32j53.cloudfront.net/embeddings/lbls_dev.npy -O vlslice/server/data/lbls_dev.npy

# ~16GB, can take some time to load, even with enough RAM.
# Labels are used for pre-filtering OpenImages as described in Section 4.1.
wget https://d30mxw38m32j53.cloudfront.net/embeddings/embs_all.npy -O vlslice/server/data/embs_all.npy
wget https://d30mxw38m32j53.cloudfront.net/embeddings/lbls_all.npy -O vlslice/server/data/lbls_all.npy

# 2. Install Python dependencies with Conda
conda env create -f environment.yml
conda activate vlslice

# 3. Run the server: http://127.0.0.1:5000
cd vlslice/server
python server.py
```

The server should now be running locally and can be accessed at: [http://127.0.0.1:5000](http://127.0.0.1:5000).
