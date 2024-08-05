import pyrootutils

root = str(pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git", ],
    pythonpath=True,
    dotenv=True))

import hydra
from src.utils.proxy import setup_proxy
from src.parsers.zotero import ZoteroLibrary, ZoteroItem
from src.utils.folders import cleanup


@hydra.main(version_base="1.2", config_path=root + "/configs", config_name="config.yaml")
def main(cfg):
    # Set up the proxy
    setup_proxy(cfg.proxy)

    # Load from id
    if cfg.id:
        item = ZoteroItem.from_identifier(cfg.id)

    # Load from url
    elif cfg.url:
        item = ZoteroItem.from_url(cfg.url)

    # Load an entire Zotero library, may take a few seconds...
    elif cfg.zotero.upload:
        item = ZoteroLibrary(cfg.zotero, verbose=cfg.verbose)

    # Fallback message
    else:
        print(
            "NoRA did not receive any argument. Please use `id=...` or "
            "`url=...` to specify a paper to be uploaded.")
        item = None

    # Upload data to NoRA
    if item is not None:
        item.to_notion(cfg.notion, verbose=cfg.verbose)

    # Dirty hack to remove the pesky folders
    cleanup(root)

if __name__ == "__main__":
    main()
