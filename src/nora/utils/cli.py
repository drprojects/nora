import click
from nora.utils.config import load_config, configure_private_config
from nora.parsers.zotero import ZoteroLibrary, ZoteroItem


@click.group()
def cli():
    """NoRA – Notion Research Assistant"""
    pass


# -------------------------------------------------------------------------
#  nora configure
# -------------------------------------------------------------------------
@cli.command()
def configure():
    """Set up your API keys and Notion/Zotero configuration."""
    configure_private_config()


# -------------------------------------------------------------------------
#  nora url ...
# -------------------------------------------------------------------------
@cli.command("url")
@click.argument("url")
def url_command(url):
    """Process a paper from its URL (e.g., arXiv, DOI)."""
    cfg = load_config()

    # Load from url
    item = ZoteroItem.from_url(url)

    # Upload data to NoRA
    if item is not None:
        item.to_notion(cfg.notion, verbose=cfg.verbose)


# -------------------------------------------------------------------------
#  nora id ...
# -------------------------------------------------------------------------
@cli.command("id")
@click.argument("id")
def id_command(id):
    """Process a Notion item by its ID."""
    cfg = load_config()

    # Load from url
    item = ZoteroItem.from_identifier(id)

    # Upload data to NoRA
    if item is not None:
        item.to_notion(cfg.notion, verbose=cfg.verbose)


# -------------------------------------------------------------------------
#  nora zotero-upload
# -------------------------------------------------------------------------
@cli.command("zotero-upload")
def zotero_upload_command():
    """Upload items to Zotero."""
    click.echo("📚 Uploading Zotero to NoRA")

    cfg = load_config()

    # Load from url
    item = ZoteroLibrary(cfg.zotero, verbose=cfg.verbose)

    # Upload data to NoRA
    if item is not None:
        item.to_notion(cfg.notion, verbose=cfg.verbose)
