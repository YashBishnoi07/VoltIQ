import random

import numpy as np


def set_global_seed(seed: int) -> None:
    """Fix all random seeds for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch  # noqa: F401

        torch.manual_seed(seed)
    except ImportError:
        pass
