import numpy as np
from scipy import stats
import torch
from transformers import CLIPProcessor, CLIPModel


class VLSliceModel(torch.nn.Module):
    def __init__(self, version, device):
        super().__init__()
        self.processor = CLIPProcessor.from_pretrained(version)
        self.model = CLIPModel.from_pretrained(version)
        self.device = device
        self.to(device)

    def forward(self, img=None, txt=None):
        if img is None and txt is None:
            raise ValueError('Both img and txt cannot be None.')

        inp = self.processor(text=txt, images=img, return_tensors='pt', padding=True)

        if txt is not None:
            with torch.no_grad():
                outs = self.model.text_model(
                    input_ids=inp.input_ids.to(self.device),
                    attention_mask=inp.attention_mask.to(self.device),
                )

            embs = self.model.text_projection(outs[1])
            embs = embs / embs.norm(dim=-1, keepdim=True)
            txt_embs = embs.detach().cpu().numpy()

        if img is not None:
            with torch.no_grad():
                outs = self.model.vision_model(
                    pixel_values=inp.pixel_values.to(self.device),
                )

            embs = self.model.visual_projection(outs[1])
            embs = embs / embs.norm(dim=-1, keepdim=True)
            img_embs = embs.detach().cpu().numpy()

        if txt is None:
            return img_embs
        if img is None:
            return txt_embs
        return txt_embs, img_embs


def load_model(version, device):
    model = VLSliceModel(version, device)
    model.eval()
    return model


def clip_sim(txt_embs, img_embs):
    sims = np.matmul(txt_embs, img_embs.transpose())
    sims = (sims + 1.0) / 2.0
    return sims.transpose()


def delta_c(sims):
    p1 = stats.rankdata(sims[:, 1]) / sims.shape[0]
    p0 = stats.rankdata(sims[:, 0]) / sims.shape[0]
    return p1 - p0
