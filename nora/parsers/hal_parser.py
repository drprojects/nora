import requests
import xmltodict
from nora.utils.venues import VENUES
from nora.parsers.notion_parser import NotionLibrary


__all__ = ['HALItem']


# Documentation: https://api.archives-ouvertes.fr/docs/search


class HALItem:

    API_URL = "http://api.archives-ouvertes.fr/search/"
    RETURN_KEYS = ','.join([
        'title_s',
        'authFullName_s',
        'abstract_s',
        'producedDateY_i',
        'halId_s',
        'label_bibtex',
        'bookTitle_s',
        'journalTitle_s',
        'conferenceTitle_s'])

    def __init__(self, hal_id=None, title=None):
        """Object to query a paper from HAL.

        :param hal_id: str
            HAL identifier, or HAL url, from which the identifier
            will be parsed. The identifier must have the format
            'hal-xxxxxxxx'
        :param title: str
            Title - or portion of the title - of the paper. The HAL
            database will be queried. NB: sometimes too long
            titles may not work so well, in which case querying only
            part of the title may solve the problem
        """
        assert hal_id is not None or title is not None, \
            "Please provide HAL identifier or a paper title"

        if hal_id is not None:
            hal_id = str(hal_id)
            if 'hal.science' in hal_id:
                hal_id = hal_id.split('/')[-1]
            query = f"halId_s:{hal_id}"

        if title is not None:
            query = f"title_t:\"{title}\""

        url = f"{self.API_URL}?q={query}&wt=xml&fl={self.RETURN_KEYS}"
        result = xmltodict.parse(requests.get(url).content)['response']['result']

        if int(result['@numFound']) == 0:
            raise ValueError(f"Could not find paper with '{query}'")

        self._result = result


    @property
    def title(self):
        return self._parse_results('arr', 'title_s')

    @property
    def authors(self):
        return self._parse_results('arr', 'authFullName_s')

    @property
    def abstract(self):
        return self._parse_results('arr', 'abstract_s')

    @property
    def venue(self):
        # Search if conferenceTitle_s, journalTitle_s, or bookTitle_s
        # have been populated
        for k in ['conferenceTitle_s', 'journalTitle_s', 'bookTitle_s']:
            v = self._parse_results('str', k)
            if v is None:
                continue
            for key, venue in VENUES.items():
                if key in v.lower():
                    return venue

    @property
    def year(self):
        return int(self._parse_results('int', 'producedDateY_i'))

    @property
    def notes(self):
        return ''

    @property
    def hal_id(self):
        return self._parse_results('str', 'halId_s')

    @property
    def url(self):
        return f"https://hal.science/{self.hal_id}"

    @property
    def bibtex(self):
        return self._parse_results('str', 'label_bibtex')

    def _parse_results(self, field, key):
        field_list = self._result['doc'][field]
        if not isinstance(field_list, list):
            field_list = [field_list]
        for x in field_list:
            if x['@name'] == key:
                sfield = 'str' if field == 'arr' else '#text'
                return x[sfield]
        return None

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
            for key in ['hal_id', 'title', 'authors']]
        return f"{self.__class__.__name__}({', '.join(info)})"
