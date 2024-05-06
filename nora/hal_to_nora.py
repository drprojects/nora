import pyrootutils

root = str(pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git", ],
    pythonpath=True,
    dotenv=True))

import hydra
from nora.utils.proxy import setup_proxy
from nora.parsers.hal_parser import HALItem


@hydra.main(version_base="1.2", config_path=root + "/configs", config_name="config.yaml")
def main(cfg):
    # Setup the proxy
    setup_proxy(cfg.proxy)

    # Recover the paper data from the arxiv API
    hitem = HALItem(hal_id=cfg.hal.id, title=cfg.hal.title)

    # Upload the paper to NoRA
    hitem.to_notion(cfg.notion)


if __name__ == "__main__":
    main()
