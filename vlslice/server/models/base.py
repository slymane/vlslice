from abc import ABC, abstractmethod

from numpy.typing import ArrayLike
from scipy import stats
import torch


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

def delta_c(sims: ArrayLike) -> ArrayLike:
    p1 = stats.rankdata(sims[:, 1]) / sims.shape[0]
    p0 = stats.rankdata(sims[:, 0]) / sims.shape[0]
    return p1 - p0
