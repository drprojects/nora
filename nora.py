import pyrootutils

root = str(pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git", ],
    pythonpath=True,
    dotenv=True))

import hydra
from src.utils.proxy import setup_proxy
from src.parsers.arxiv import ArxivItem
from src.parsers.elsevier import ElsevierItem
from src.parsers.springer import SpringerItem
from src.parsers.hal import HALItem
from src.parsers.zotero import ZoteroLibrary
from src.utils.folders import cleanup


@hydra.main(version_base="1.2", config_path=root + "/configs", config_name="config.yaml")
def main(cfg):
    # Set up the proxy
    setup_proxy(cfg.proxy)

    # Load an arxiv paper
    if cfg.arxiv.id or cfg.arxiv.title:
        item = ArxivItem(arxiv_id=cfg.arxiv.id, title=cfg.arxiv.title)

    # Load an Elsevier paper
    elif cfg.elsevier.id or cfg.elsevier.doi:
        item = ElsevierItem(cfg.elsevier.api_key, id=cfg.elsevier.id, doi=cfg.elsevier.doi)

    # Load a Springer paper
    elif cfg.springer.doi or cfg.springer.url:
        item = SpringerItem(cfg.springer.api_key, doi=cfg.springer.doi, url=cfg.springer.url)

    # Load a HAL paper
    elif cfg.hal.id or cfg.hal.title:
        item = HALItem(hal_id=cfg.hal.id, title=cfg.hal.title)

    # Load an entire Zotero library, may take a few seconds...
    elif cfg.zotero.upload:
        item = ZoteroLibrary(cfg.zotero, verbose=cfg.verbose)

    # Fallback message
    else:
        print("Did not receive any argument requiring an upload to NORA")
        item = None

    # Upload data to NORA
    if item is not None:
        item.to_notion(cfg.notion, verbose=cfg.verbose)

    # Dirty hack to remove the pesky folders
    cleanup(root)

if __name__ == "__main__":
    main()
