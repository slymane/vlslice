import base64
import io

from PIL import Image
import numpy as np


def img2b64(img_idx, images):
    image = Image.fromarray(images[img_idx])

    # save image object to bytes stream
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')

    data = base64.encodebytes(buffer.getvalue()).decode('ascii')
    return data


def cart(arrays):
    la = len(arrays)
    arr = np.empty([la] + [len(a) for a in arrays], dtype=int)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[i, ...] = a
    return arr.reshape(la, -1)
