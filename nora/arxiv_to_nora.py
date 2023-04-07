import pyrootutils

root = str(pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git", ],
    pythonpath=True,
    dotenv=True))

import hydra
from nora.utils.proxy import setup_proxy
from nora.parsers.arxiv_parser import ArxivItem


@hydra.main(version_base="1.2", config_path=root + "/configs", config_name="config.yaml")
def main(cfg):
    # Setup the proxy
    setup_proxy(cfg.proxy)

    # Recover the paper data from the arxiv API
    xitem = ArxivItem(arxiv_id=cfg.arxiv.id, title=cfg.arxiv.title)

    # Upload the paper to NoRA
    xitem.to_notion(cfg.notion)


if __name__ == "__main__":
    main()
