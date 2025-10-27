import sys


__all__ = ['sanity_check_config']


def sanity_check_config(cfg, keys, expected_keys):
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
