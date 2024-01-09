# VLSlice

VLSlice is an interactive system enabling user-guided discovery of Vision-Language Slices, coherent representation-level subgroups with consistent visiolinguistic behavior, from unlabeled image sets. Slices can help identify problematic behaviors and biases learned by web-scale pretrained models. VLSlice supports users in discovering and refining slices along arbitrary bias dimensions while leveraging those slices to assist them in validating model behavior.

<p align="center">
  <img src="./media/vlslice.png">
  <a href="https://arxiv.org/abs/2309.06703">[ pdf ]</a>
  <a href="https://ericslyman.com/assets/pdf/vlslice_poster.pdf">[ poster ]</a>
  <a href="https://drive.google.com/file/d/1mOuvjphNb2xNDC7shoGbPwyjbfArwud4/view?usp=drive_link">[ iccv talk ]</a>
  <a href="https://www.youtube.com/watch?v=2CMDcGGsMjo&list=PLUxOP3kBxs2JYA5KT0YEmNJEyjqAqLOf3&index=1">[ showcase talk ]</a>
  <a href="https://drive.google.com/file/d/1JkbVXnCds6rOErUx-YWZmp3mQ3IDJuhi/view?usp=drive_link">[ video demo ]</a>
  <a href="https://ericslyman.com/vlslice/">[ website ]</a>
</p>

## Getting Started

The VLSlice client is built with a JS/Svelte client running on a Python/Flask backend. To run the server, however, only the Python dependencies must be installed. The following code blocks walk through downloading precomputed image embeddings from CLIP on OpenImages, creating an appropriate Python environment with conda, and starting the VLSlice server.

We provide demo data for running VLSlice at [oregonstate.box.com/v/vlslice-demo](https://oregonstate.box.com/v/vlslice-demo). This data contains the first million boxes extracted from OpenImages according the process described in our paper.

```bash
# 1. Download Data
# Labels are used for pre-filtering OpenImages as described in Section 4.1.
cd vlslice/server/static/
mv [all files downloaded from box] ./
tar xf images.tar.gz && rm images.tar.gz
cd -

# 2. Install Python dependencies with Conda
conda env create -f environment.yml
conda activate vlslice

# If using an Intel CPU, sklearn intelex can speed up clustering (optional)
conda install scikit-learn-intelex=2021.4.0

# 3. Run the server: http://127.0.0.1:5000
cd vlslice/server
python server.py
```

The server should now be running locally and can be accessed at [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Configuration

Our code can be used with any ViL model that separately embeds images and text, and any image dataset. All that is required is an array of precomputed image embeddings, image URLs, and modifying the forward pass in [model.py](vlslice/server/model.py) to use your model.

### Configuring Flask

All properties set under `flask` in the [config.yml](vlslice/server/config.yml) are automatically passed as a dictionary unpacked into the flask `app.run()` call. Set whichever settings you wish for flask to use here.

### Faster Image Loading

Serving images from the [/static/](./vlslice/server/static/) folder with the built-in flask server (e.g., the example above) can lead to slow image loading. This can be mitigated by either moving images behind a CDN or by using a more sophisticated web server. During our user study, we used AWS [CloudFront](https://aws.amazon.com/cloudfront/) to deliver images stored on [S3](https://aws.amazon.com/s3/) and a [gunicorn](https://gunicorn.org/) web server. **We describe recommended steps for setting up a more sophisticated web server below which should be used for anything beyond the most basic exploration with VLSlice.**

First, install and start a [gunicorn](https://gunicorn.org/) WSGI server from inside [vlslice/server](./vlslice/server/). The `-w` argument specifies the number of server processes.

```bash
pip install gunicorn
gunicorn --bind localhost:5000 -w 2 server:app
```

Then, install [nginx](https://www.nginx.com/) to use as our reverse proxy. You will need to allow it firewall HTTP access.

```bash
sudo apt update
sudo apt install nginx
sudo ufw allow 'Nginx HTTP'
```

We will create a new nginx site for VLSlice:

```bash
sudo nano /etc/nginx/sites-available/vlslice
```

Paste the following site configuration with the absolute path to your VLSlice [static](./vlslice/server/static/) folder,
or whatever other location you've chosen to store the images specified by `imgs.npy`, under `location /static > alias`.

```yaml
server {
    listen 5050;
    server_name localhost;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static {
        alias [ABSOLUTE PATH TO YOUR STATIC FOLDER];
        expires 7d;
    }
}
```

Link the VLSlice site to active and restart nginx:

```bash
sudo ln -s /etc/nginx/sites-available/vlslice /etc/nginx/sites-enabled
sudo systemctl restart nginx
```

You should now be able to navigate to `localhost:5050` in a web browser and use VLSlice with significantly faster image loading.

### Using Your Own Data

To configure your own data, specify three numpy files in the [config.yml](vlslice/server/config.yml):

```yaml
data:
  # ndarray[string] (N) containing N image paths. 
  # e.g., "https://d30mxw38m32j53.cloudfront.net/00000000.jpg"
  imgs_npy: ./static/imgs.npy  
  
  # ndarray[string] (N) containing N image classes. 
  # Set to "null" to disable filtering.
  lbls_npy: ./static/lbls.npy  

  # ndarray[float] (NxD) containing N image embeddings of size D.
  embs_npy: ./static/embs.npy  
```

VLSlice will use these files to load, filtering, and cluster your images. All files are expected to share the same index order. If you wish to exclude any class of images from display in VLSlice (e.g., to remove redundant subparts of people), then the target class to be removed may be specified under `exclude_classes`.

### Using Your Own Model

To configure your own model, specify the `name` and `configuration` of the model under the [config.yml](vlslice/server/config.yml):

```yaml
data:
  # Name of the model to load
  name: hf_clip

  # Configuration options to pass to model initialization
  config:
    version: openai/clip-vit-base-patch16
    device: cpu
```

You may add your own model by extending the base [VLSliceModel](vlslice/server/models/base.py) class and adding a corresponding model name to the [model registry](vlslice/server/models/__init__.py). Properties under `config` will automatically be passed to your model during initialization. For an example, see [HFCLIP.py](vlslice/server/models/HFCLIP.py), where we register a HuggingFace CLIP model.

```python
class VLSliceModel(ABC, torch.nn.Module):

    @classmethod
    @abstractmethod
    def similarity(cls, txt_embs: ArrayLike, img_embs: ArrayLike) -> ArrayLike:
        """Calculate text-image similarity scores normalized to the range [0, 1].

        Args:
            txt_embs (ArrayLike): N_t text embeddings.
            img_embs (ArrayLike): N_i image embeddings.

        Returns:
            ArrayLike: N_t x N_i similarity scores.
        """
        pass

    @abstractmethod
    def forward(self, txt: list[str]) -> ArrayLike:
        """Extract text embeddings.

        Args:
            txt (list[str]): List of N strings to embed.

        Returns:
            ArrayLike: Outputted NxD text embeddings.
        """
        pass
```

**Note that the model used in VLSlice should be the same model used to extract `embs_img.npy`.**

## Development

To develop the client interface, first install npm and Node.js. Then, run the following commands after making edits to the interface. No special setup is required beyond installing the conda environment to develop the server.

```bash
# Install packages
cd vlslice/client
npm install

# Choose one...
# Build once.
npm run build

# Build and check for updates.
npm run autobuild
```

## Troubleshooting

Tokenizers may fail to install on Apple Silicon machines due to the rust compiler missing. The compiler can be installed with the following command:

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source "$HOME/.cargo/env"
```

Then install the environment with Conda as described above. Conda and Pip can take some time with this installation.

## Citation

```bibtex
@InProceedings{Slyman_2023_ICCV,
    author    = {Slyman, Eric and Kahng, Minsuk and Lee, Stefan},
    title     = {VLSlice: Interactive Vision-and-Language Slice Discovery},
    booktitle = {Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)},
    month     = {October},
    year      = {2023},
    pages     = {15291-15301}
}
```
