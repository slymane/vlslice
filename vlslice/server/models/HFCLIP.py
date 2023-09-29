import numpy as np
import torch
from transformers import CLIPProcessor, CLIPModel

from models.base import VLSliceModel


class HFClipModel(VLSliceModel):
    def __init__(self, version, device):
        super().__init__()
        self.processor = CLIPProcessor.from_pretrained(version)
        self.model = CLIPModel.from_pretrained(version)
        self.device = device
        self.to(device)

    @staticmethod
    def similarity(txt_embs, img_embs):
        sims = np.matmul(txt_embs, img_embs.transpose())
        sims = (sims + 1.0) / 2.0
        return sims.transpose()

    def forward(self, txt):
        inp = self.processor(text=txt, return_tensors='pt', padding=True)
        with torch.no_grad():
            outs = self.model.text_model(
                input_ids=inp.input_ids.to(self.device),
                attention_mask=inp.attention_mask.to(self.device),
            )

            embs = self.model.text_projection(outs[1])
            embs = embs / embs.norm(dim=-1, keepdim=True)
            txt_embs = embs.detach().cpu().numpy()

        return txt_embs
