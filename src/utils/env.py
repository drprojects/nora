import sys


__all__ = ['sanity_check_config']


def sanity_check_config(cfg, keys, env_variables):
    missing_env_variables = [
        v for k, v in zip(keys, env_variables)
        if getattr(cfg, k, '???') == '???']
    if len(missing_env_variables) == 0:
        return
    print(
        "🛑  Missing required environment variables. Please create a "
        "`.env` file in your NoRA project's root directory and "
        "declare in there the following variables (cf the README "
        "instructions:\n")
    for v in missing_env_variables:
        print(f"  - {v}=XXX")
    sys.exit(1)
