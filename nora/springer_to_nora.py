import pyrootutils

root = str(pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git", ],
    pythonpath=True,
    dotenv=True))


import hydra
from nora.utils.proxy import setup_proxy
from nora.parsers.springer_parser import SpringerItem


@hydra.main(version_base="1.2", config_path=root + "/configs", config_name="config.yaml")
def main(cfg):
    # Set up the proxy
    setup_proxy(cfg.proxy)

    # Recover the paper data from the Springer API
    sitem = SpringerItem(cfg.springer.api_key, doi=cfg.springer.doi, url=cfg.springer.url)

    # Upload the paper to NoRA
    sitem.to_notion(cfg.notion)


if __name__ == "__main__":
    main()
