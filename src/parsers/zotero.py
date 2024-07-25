import datetime
from pyzotero import zotero
from src.utils.venues import VENUES
from src.parsers.arxiv import ArxivItem
from src.parsers.notion import NotionLibrary
from src.utils.translation_server import *
from src.utils.zotero import *


__all__ = ['ZoteroLibrary', 'ZoteroItem']


class ZoteroLibrary:

    def __init__(self, cfg, verbose=False):
        self.cfg = cfg
        self.verbose = verbose
        self.library = None
        self.items = None
        self.ignored = []

        # Read ALL the library, may take a few seconds...
        self.load()

        # Trim papers
        self.discard_non_paper()
        self.discard_no_authors()
        self.discard_duplicates()

    def load(self):
        """Connect to the Zotero library and read ALL OF IT. May take a
        few seconds.
        """
        if self.verbose:
            print("Loading items...")

        self.library = zotero.Zotero(
            self.cfg.library_id, 'user', self.cfg.api_token)

        self.items = self.library.everything(self.library.top())

    def discard_non_paper(self):
        """Only keep paper-type items.
        """
        if self.verbose:
            print("Discarding non-paper items...")
        ignored = [
            (item, f"non-paper dtype: {item['data']['itemType']}")
            for item in self.items
            if item['data']['itemType'] not in ZOTERO_SUPPORTED_TYPES]
        self.items = [
            item for item in self.items
            if item['data']['itemType'] in ZOTERO_SUPPORTED_TYPES]
        self.ignored += ignored
        if self.verbose:
            print(f"Found {len(ignored)} non-paper items")

    def discard_no_authors(self):
        """Only keep papers with at least 1 author.
        """
        if self.verbose:
            print("Discarding items without authors...")
        ignored = []
        ignored += [
            (item, f"no authors")
            for item in self.items if len(item['data']['creators']) < 1]
        self.items = [
            item for item in self.items if len(item['data']['creators']) > 0]
        self.ignored += ignored
        if self.verbose:
            print(f"Found {len(ignored)} items without author")

    def discard_duplicates(self):
        """Only keep the first-encountered item if multiple items have
        the same title.
        """
        if self.verbose:
            print("Discarding duplicate items...")
        ignored = []
        titles = []
        keep = []
        for i, item in enumerate(self.items):
            title = item['data']['title']
            if title in titles:
                ignored.append((item, f"duplicate title: {title}"))
                continue
            titles.append(title)
            keep.append(i)
        self.items = [self.items[i] for i in keep]
        self.ignored += ignored
        if self.verbose:
            print(f"Found {len(ignored)} duplicate items")

    def to_notion(self, cfg, verbose=True):
        """Move all papers and authors in the Zotero library to Notion.
        This may take a while...
        """
        for i, zitem in enumerate(self):
            if verbose:
                print(f"[{i + 1}/{len(self)}]", end=' ')
            zitem.to_notion(cfg, verbose=verbose)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return ZoteroItem(
            self.items[i], library=self.library,
            ignored_collections=self.cfg.ignored_collections)

    def __iter__(self):
        for i in range(len(self)):
            yield self[i]

    def __repr__(self):
        return f"{self.__class__.__name__}({len(self)})"


class ZoteroItem:

    def __init__(self, item, library=None, ignored_collections=None):
        self.item = item
        self.library = library

        self.notes = self.get_notes()
        self.tags = self.get_tags(ignored_collections)
        self.venue = self.get_venue()

    @classmethod
    def from_url(cls, url, **kwargs):
        """Retrieve metadata for a webpage. This mimics the behavior of
        the Zotero plugin for adding pages from the browser.
        """
        return cls(translate_from_url(url, **kwargs))

    @classmethod
    def from_identifier(cls, identifier, **kwargs):
        """Retrieve metadata from an identifier (DOI, ISBN, PMID, arXiv
        ID). Note that for some of these identifiers, the parsed
        libraries may not provide as extensive metadata as when parsing
        from the web page with `translate_from_url`. This is typically
        the case when using the DOI: the crossref database will be used,
        which usually does not provide paper abstracts.
        """
        return cls(translate_from_identifier(identifier, **kwargs))

    @property
    def key(self):
        return self.item['key']

    @property
    def type(self):
        return self.item['data']['itemType']

    @property
    def title(self):
        return self.item['data']['title']

    @property
    def abstract(self):
        return self.item['data'].get('abstractNote', '')

    @property
    def url(self):
        return self.item['data']['url']

    @property
    def arxiv(self):
        if 'arxiv.org' in self.url:
            return self.url.split('/')[-1]

    @property
    def authors(self):
        return [
            (creator['firstName'], creator['lastName'])
            for creator in self.item['data']['creators']
            if 'firstName' in creator.keys() and 'lastName' in creator.keys()]

    @property
    def to_read(self):
        for tag in self.item['data']['tags']:
            if tag['tag'].upper() == 'TO READ':
                return True
        return False

    @property
    def year(self):
        # See Zotero documentation for fields:
        date = None
        for key in ZOTERO_DATE_FIELDS:
            if key in self.item['data'].keys():
                date = self.item['data'][key]
                break

        if date is None or len(date) == 0:
            return None

        if date.isnumeric():
            return int(date)

        try:
            return datetime.datetime.fromisoformat(date).year
        except:
            pass

        sep = None
        for s in '-/*., ':
            if s in date:
                sep = s
                break

        if sep is None:
            return None

        for x in date.split(sep):
            if x.isnumeric() and len(x) == 4:
                return int(x)

        return None

    def get_notes(self):
        notes = ''

        if 'meta' not in self.item.keys():
            return notes

        if self.item['meta']['numChildren'] == 0:
            return notes

        if self.library is None:
            return notes

        for child in self.library.children(self.key):
            if child['data']['itemType'] != 'note':
                continue
            notes += child['data']['note'] + '\n\n\n'

        return notes

    def get_tags(self, ignored_collections=None):
        """This is HACKY and specific to my needs: I do not use the
        Zotero tags but the collections instead. Besides, I exclude some
        collection names which are not useful to me.
        """
        tags = []
        if 'collections' not in self.item['data'].keys():
            return tags
        for key in self.item['data']['collections']:
            tags += self.get_collection_ancestors(key)
        # tags = list(set(tags))
        if ignored_collections is not None:
            tags = [t for t in tags if t not in ignored_collections]
        return tags

    def get_collection_ancestors(self, key):
        names = []
        if self.library is None:
            return names
        collection = self.library.collection(key)
        names.append(collection['data']['name'])
        parent_key = collection['data']['parentCollection']
        if parent_key:
            names += self.get_collection_ancestors(parent_key)
        return names

    def get_venue(self):
        # Search in the item-type specific fields first
        fallback_text = None
        for field in ZOTERO_VENUE_FIELDS:
            if field not in self.item['data'].keys():
                continue
            text = self.item['data'][field]
            fallback_text = text if not fallback_text else fallback_text
            for key, venue in VENUES.items():
                if key in text.lower():
                    return venue

        # Search in the notes
        for key, venue in VENUES.items():
            if key in self.notes.lower():
                return venue

        # Search venue on arXiv
        if self.arxiv is not None and self.arxiv != '':
            return ArxivItem(self.arxiv).venue

        return fallback_text

    def to_notion(self, cfg, verbose=True):
        """Move paper and authors to Notion. Takes a few seconds...
        """
        if verbose:
            print(f"Uploading '{self.title}'...", end=' ')

        # First, create the paper and its properties
        response = NotionLibrary(cfg).create_paper(
            self.title,
            authors=[f"{x[0]} {x[1]}" for x in self.authors],
            topics=self.tags,
            to_read=self.to_read,
            abstract=self.abstract,
            url=self.url,
            year=self.year,
            venue=self.venue)

        # Second, create the blocks (free text) from the notes
        if response is not None and self.notes is not None and self.notes != '':
            paper_id = response.json()['id']
            NotionLibrary(cfg).append_page_blocks(paper_id, self.notes)

        if verbose:
            print('Done')

    def __repr__(self):
        info = [
            f"{key}={getattr(self, key)}"
            for key in ['key', 'title', 'authors']]
        return f"{self.__class__.__name__}({', '.join(info)})"
