from scholarly import scholarly
from scholarly import ProxyGenerator

# Documentation: https://scholarly.readthedocs.io

# TODO: wanted to use scholarly to parse bibtex, but could not get it to
#  work yet and risk of seeing my IP being blocked due to too-many API
#  calls

# Set up a ProxyGenerator object to use free proxies
# This needs to be done only once per session
def setup_scholar_proxy(cfg):
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)
    pg.SingleProxy(http=cfg.proxy.http_proxy, https=cfg.proxy.https_proxy)
    return pg
