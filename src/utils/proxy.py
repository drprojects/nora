import os

__all__ = ['setup_proxy']

def setup_proxy(cfg):
    if os.getenv('HTTP_PROXY') is None:
        os.environ['HTTP_PROXY'] = cfg.http_proxy
    if os.getenv('HTTPS_PROXY') is None:
        os.environ['HTTPS_PROXY'] = cfg.https_proxy
