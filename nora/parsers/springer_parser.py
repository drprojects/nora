import requests
import xmltodict
from nora.utils.venues import VENUES
from nora.parsers.notion_parser import NotionLibrary


__all__ = ['SpringerItem']


# Documentation: https://docs-dev.springernature.com/docs/


class SpringerItem:

    API_URL = "http://api.springernature.com/meta/v2/"
    DOI_PREFIX = '10.1038/'

    def __init__(self, api_key, doi=None, url=None):
        """Object to query a paper from Springer META API.

        :param api_key: string
            API key to query Springer META API database
        :param doi: str
            DOI identifier in format '.../...', or
            'https://doi.org/.../...'
        :param url: str
            URL in format 'https://www.nature.com/articles/...
            from which the DOI will be recovered

        """
        assert doi is not None or url is not None, \
            "Please provide a DOI identifier or a 'https://www.nature.com/articles/...' url"

        if doi is not None:
            doi = str(doi)
            if 'doi.org' in doi:
                doi = '/'.join(doi.split('/')[-2:])

        if url is not None:
            assert "www.nature.com/articles/" in url, \
                ("Please provide an article URL with the following format: "
                 "'https://www.nature.com/articles/...")
            doi = self.DOI_PREFIX + url.split('/')[-1]

        query_url = f"{self.API_URL}pam?q=doi:{doi}&api_key={api_key}"
        response = xmltodict.parse(requests.get(query_url).content)['response']

        if int(response['result']['total']) == 0:
            raise ValueError(f"Could not find paper with '{query_url}'")

        self._result = response['records']['record']['pam:message']['pam:article']

    @property
    def doi(self):
        return self._result['xhtml:head']['prism:doi']

    @property
    def title(self):
        return self._result['xhtml:head']['dc:title']

    @property
    def authors(self):
        # Authors are returned in "lastname, firstname" format
        authors = self._result['xhtml:head']['dc:creator']
        return [f"{x.split(', ')[1]} {x.split(', ')[0]}" for x in authors]

    @property
    def abstract(self):
        return ' '.join(self._result['xhtml:body']['xhtml:p'])

    @property
    def venue(self):
        journal = self._result['xhtml:head']['prism:publicationName']

        if journal is not None:
            for key, venue in VENUES.items():
                if key in journal.lower():
                    return venue

        return journal

    @property
    def year(self):
        return int(self._result['xhtml:head']['prism:publicationDate'].split('-')[0])

    @property
    def notes(self):
        return ''

    @property
    def url(self):
        return "https://www.nature.com/articles/" + self.doi.split('/')[-1]

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
