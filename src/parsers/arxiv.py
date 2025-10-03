import arxiv
import re
from src.utils.venues import VENUES
from src.parsers.notion import NotionLibrary


__all__ = ['ArxivItem']


# Documentation: http://lukasschwab.me/arxiv.py/index.html

# Create a Client to wrap the requests. In particular, the Client
# ensures you do not make more than 1 request every 3 seconds, which is
# the maximum request frequency explicitly required by arxiv
CLIENT = arxiv.Client(page_size=100, delay_seconds=3, num_retries=3)


class ArxivItem:

    def __init__(self, arxiv_id=None, title=None, max_results=10):
        """Object to query a paper from arxiv.

        :param arxiv_id: str
            Arxiv identifier, or arxiv url, from which the identifier
            will be parsed
        :param title: str
            Title - or portion of the title - of the paper. The arxiv
            database will be queried and the top 10 results will be
            returned
        """
        assert arxiv_id is not None or title is not None, \
            "Please provide an arxiv identifier or a paper title"

        if arxiv_id is not None:
            arxiv_id = str(arxiv_id)

            # Parse arxiv id from a url
            if 'arxiv.org' in arxiv_id:
                arxiv_id = arxiv_id.split('arxiv.org/')[-1].replace('.pdf', '')

            # Check whether arxiv id format before March 2007
            if not bool(re.search(r'[0-9]{4}\.[0-9]', arxiv_id)):
                raise ValueError(
                    f"The arxiv identifier '{arxiv_id}' does not follow the arxiv format "
                    f"defined for articles published after March 2007. At the moment, only"
                    f"articles following this pattern are supported. Please refer to:"
                    f"https://info.arxiv.org/help/arxiv_identifier.html")

            # Isolate the YYMM.NNNNN sequence
            arxiv_id = arxiv_id.split('/')[-1]

            # Sometimes trailing 0s are lost in the process. It is
            # possible to cover these cases as long as the article
            # came out after March 2007:
            # https://info.arxiv.org/help/arxiv_identifier.html
            yymm, numbervv = arxiv_id.split(':')[-1].split('.')
            expected_number_size = 5 if int(yymm) >= 1501 else 4
            if len(numbervv) < expected_number_size:
                numbervv += '0' * (expected_number_size - len(numbervv))
                arxiv_id = f"{yymm}.{numbervv}"

            self.id = arxiv_id
            results = list(CLIENT.results(arxiv.Search(id_list=[arxiv_id])))
            if len(results) == 0:
                raise ValueError(f"Could not find paper with id='{arxiv_id}'")
            self._item = results[0]
            return

        if title is not None:
            results = list(CLIENT.results(arxiv.Search(
                query=f"ti:{title}", max_results=max_results,
                sort_by=arxiv.SortCriterion.Relevance)))
            results = [res for res in results if title in res.title]
            if len(results) == 0:
                raise ValueError(f"Could not find paper with title='{title}'")
            if len(results) > 1:
                msg = f"Found multiple papers matching title='{title}'. " \
                      f"Please refine among the following:\n" + \
                      '\n'.join([res.title for res in results])
                raise ValueError(msg)
            self.id = results[0].entry_id.split('/')[-1].replace('.pdf', '')
            self._item = results[0]

    @property
    def title(self):
        return self._item.title

    @property
    def authors(self):
        return [x.name for x in self._item.authors]

    @property
    def abstract(self):
        return self._item.summary

    @property
    def venue(self):
        # Search venue in 'journal_ref'
        if self._item.journal_ref is not None:
            for key, venue in VENUES.items():
                if key in self._item.journal_ref.lower():
                    return venue

        # Search venue in 'comment'
        if self.notes is not None:
            for key, venue in VENUES.items():
                if key in self.notes.lower():
                    return venue

        return self._item.journal_ref

    @property
    def year(self):
        return self._item.published.year

    @property
    def notes(self):
        return self._item.comment

    @property
    def url(self):
        return f"http://arxiv.org/abs/{self.id}"

    @property
    def doi(self):
        return self._item.doi

    def to_notion(self, cfg, verbose=True):
        """Move paper and authors to Notion. Takes a few seconds...
        """
        if verbose:
            print(f"⬆️  Uploading '{self.title}'...")

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
            print('✅ Done')

    def __repr__(self):
        info = [
            f"{key}={getattr(self, key)}"
            for key in ['id', 'title', 'authors']]
        return f"{self.__class__.__name__}({', '.join(info)})"
