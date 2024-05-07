import pyrootutils

root = str(pyrootutils.setup_root(
    search_from=__file__,
    indicator=[".git", ],
    pythonpath=True,
    dotenv=True))

import os
import hydra
import shutil
import tempfile
from nora.utils.proxy import setup_proxy
from elsapy.elsclient import ElsClient
from nora.parsers.elsevier_parser import ElsevierItem


@hydra.main(version_base="1.2", config_path=root + "/configs", config_name="config.yaml")
def main(cfg):
    # Set up the proxy
    setup_proxy(cfg.proxy)

    def cleanup():
        # Dirty hack to remove the pesky folders created by elsapy
        for dirname in ['data', 'logs']:
            path = os.path.join(root, dirname)
            if os.path.exists(path) and os.path.isdir(path):
                shutil.rmtree(path)

    try:
        # Set up th ElsevierClient
        client = ElsClient(cfg.elsevier.api_key, local_dir=tempfile.TemporaryDirectory().name)

        # Recover the paper data from the Elsevier API
        eitem = ElsevierItem(client, id=cfg.elsevier.id, doi=cfg.elsevier.doi)

        # Upload the paper to NoRA
        eitem.to_notion(cfg.notion)

        cleanup()

    except:
        cleanup()


if __name__ == "__main__":
    main()
