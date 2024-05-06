import elsapy
from elsapy.elsdoc import FullDoc, AbsDoc
from nora.utils.venues import VENUES
from nora.parsers.notion_parser import NotionLibrary


__all__ = ['ElsevierItem']


# Documentation: https://github.com/ElsevierDev/elsapy


class ElsevierItem:

    def __init__(self, client, id=None, doi=None):
        """Object to query a paper from Elsevier.

        :param client: ElsClient
            elsapy ElsClient object, initialized with an API token.
        :param id: str
            Elsevier PII identifier, or url, from which the
            identifier will be parsed
        :param id: str
            Paper DOI
        """
        assert id is not None or doi is not None, \
            "Please provide an Elsevier identifier, or DOI"

        if id is not None:
            if "sciencedirect.com" in id:
                id = id.split('/')[-1]
            self._full_doc = FullDoc(sd_pii=id)

        if doi is not None:
            if "doi.org" in doi:
                doi = doi.split('doi.org/')[-1]
            self._full_doc = FullDoc(doi=doi)

        self._full_doc.read(client)
        self._abs_doc = AbsDoc(
            scp_id=self._full_doc.data['link']['@href'].split('/')[-1])
        self._abs_doc.read(client)

    @property
    def title(self):
        return self._abs_doc.title

    @property
    def authors(self):
        return [
            f"{x['ce:given-name']} {x['ce:surname']}"
            for x in self._abs_doc.data['authors']['author']]

    @property
    def abstract(self):
        return self._abs_doc.data['coredata']['dc:description']

    @property
    def venue(self):
        journal = self._abs_doc.data['coredata']['prism:publicationName']

        # Search venue in 'journal_ref'
        if journal is not None:
            for key, venue in VENUES.items():
                if key in journal.lower():
                    return venue

        return journal

    @property
    def year(self):
        return int(self._abs_doc.data['coredata']['prism:coverDate'].split('-')[0])

    @property
    def notes(self):
        return ''

    @property
    def url(self):
        pii = self._abs_doc.data['coredata']['pii']
        return f"https://sciencedirect.com/science/article/pii/{pii}"

    @property
    def doi(self):
        return self._full_doc.id

    def to_notion(self, cfg, verbose=True):
        """Move paper and authors to Notion. Takes a few seconds...
        """
        if verbose:
            print(f"Uploading '{self.title}'...", end=' ')

        # First, create the paper and its properties
        response = NotionLibrary(cfg).create_paper(
            self.title,
            authors=self.authors,
            topics=[],
            to_read=True,
            abstract=self.abstract,
            url=self.url,
            year=self.year,
            venue=self.venue)

        # Second, create the blocks (free text) from the notes
        if response is not None and self.notes is not None:
            paper_id = response.json()['id']
            NotionLibrary(cfg).append_page_blocks(paper_id, self.notes)

        if verbose:
            print('Done')

    def __repr__(self):
        info = [
            f"{key}={getattr(self, key)}"
            for key in ['doi', 'title', 'authors']]
        return f"{self.__class__.__name__}({', '.join(info)})"
