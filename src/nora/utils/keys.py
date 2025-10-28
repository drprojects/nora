import sys
from omegaconf import OmegaConf
from typing import List


__all__ = ['sanity_check_config']


def sanity_check_config(
        cfg: OmegaConf,
        keys: List[str],
        expected_keys: List[str]):
    missing_keys = [
        v for k, v in zip(keys, expected_keys)
        if getattr(cfg, k, '???') == '???']
    if len(missing_keys) == 0:
        return
    print(
        "🛑 Missing private keys. Please run `nora configure` to set up "
        "your private keys:\n")
    for v in missing_keys:
        print(f"  - {v}=XXX")
    sys.exit(1)
