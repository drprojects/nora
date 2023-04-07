import pyrootutils

root = str(pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git", ],
    pythonpath=True,
    dotenv=True))

import hydra
from nora.utils.proxy import setup_proxy
from nora.parsers.zotero_parser import ZoteroLibrary


@hydra.main(version_base="1.2", config_path=root + "/configs", config_name="config.yaml")
def main(cfg):
    # Setup the proxy
    setup_proxy(cfg.proxy)

    # Load all your Zotero library, may take a fex seconds...
    z = ZoteroLibrary(cfg.zotero, verbose=True)

    # Upload all the Zotero library to NoRA
    z.to_notion(cfg.notion, verbose=True)


if __name__ == "__main__":
    main()
