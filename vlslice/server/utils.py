import base64
import io

from PIL import Image
import numpy as np


def img2b64(img_idx, boxes):
    image = Image.fromarray(boxes[img_idx])

    # save image object to bytes stream
    output = io.BytesIO()
    image.save(output, format='PNG')

    # encode bytes as base64 string
    b64 = str(base64.b64encode(output.getvalue()).decode('utf-8'))
    return b64


def img2html(img_idx, boxes, size=112, margin=3):
    return f'''<img
        src='data:image/png;base64,{img2b64(img_idx, boxes)}'
        width='{size}' height='{size}' 
        style='margin:0px {margin}px 0px {margin}px;'/>
    '''


def cart(arrays):
    la = len(arrays)
    arr = np.empty([la] + [len(a) for a in arrays], dtype=int)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[i, ...] = a
    return arr.reshape(la, -1)

