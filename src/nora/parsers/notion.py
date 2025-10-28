import requests
import mistletoe
from notional.parser import HtmlParser
from omegaconf import OmegaConf
from typing import List, Dict

from nora.utils.keys import sanity_check_config


__all__ = ['NotionLibrary']


class NotionLibrary:

    """Holds all static methods for interacting with your Notion
    databases.

    Inspired by:
        https://developers.notion.com/docs/create-a-notion-integration
        python-engineer.com/posts/notion-api-python
        https://developers.notion.com/reference/post-database-query
    """

    # TODO: automatically generate bibtex from notion (maybe parse arxiv first)

    def __init__(self, cfg: OmegaConf):
        keys = [
            'token',
            'papers_db_id',
            'people_db_id',
            'affiliations_db_id',
            'venues_db_id',
            'topics_db_id']
        private_keys = [f"notion_{k}" for k in keys]
        sanity_check_config(cfg, keys, private_keys)

        self.cfg = cfg
        self.headers = {
            "authorization": "Bearer " + self.cfg.token,
            "Notion-Version": "2022-06-28",
            "content-type": "application/json"}

    def retrieve_page_from_id(self, page_id: str):
        """Directly retrieve a page from its id.
        """
        url = f"https://api.notion.com/v1/pages/{page_id}"
        response = requests.get(url, headers=self.headers)
        if response.text['object'] != 'error':
            return response.json()

    def _get_pages(
            self,
            database_id: str,
            num: int=None,
            name_equals: str=None,
            name_contains: str=None):
        """Get pages from your Notion database.

        credits: https://www.python-engineer.com/posts/notion-api-python
        """

        # Initialization
        url = f"https://api.notion.com/v1/databases/{database_id}/query"
        get_all = num is None
        num = 100 if get_all else num

        # Read first batch of 'num' pages
        payload = {"page_size": num}
        if name_equals:
            payload['filter'] = {
                "property": "Name",
                "rich_text": {
                    "equals": name_equals}}
        elif name_contains:
            payload['filter'] = {
                "property": "Name",
                "rich_text": {
                    "contains": name_contains}}
        response = requests.post(url, json=payload, headers=self.headers)
        data = response.json()
        results = data["results"]

        # If more is needed, read other chunks of 'num' pages
        while data["has_more"] and get_all:
            payload["start_cursor"] = data["next_cursor"]
            response = requests.post(
                url, json=payload, headers=self.headers)
            data = response.json()
            results.extend(data["results"])

        return results

    def get_people(self, *args, **kwargs):
        """Get person pages from your Notion database.
        """
        return self._get_pages(self.cfg.people_db_id, *args, **kwargs)

    def get_papers(self, *args, **kwargs):
        """Get paper pages from your Notion database.
        """
        return self._get_pages(self.cfg.papers_db_id, *args, **kwargs)

    def get_affiliations(self, *args, **kwargs):
        """Get affiliation pages from your Notion database.
        """
        return self._get_pages(self.cfg.affiliations_db_id, *args, **kwargs)

    def get_venues(self, *args, **kwargs):
        """Get venue pages from your Notion database.
        """
        return self._get_pages(self.cfg.venues_db_id, *args, **kwargs)

    def get_topics(self, *args, **kwargs):
        """Get topic pages from your Notion database.
        """
        return self._get_pages(self.cfg.topics_db_id, *args, **kwargs)

    def get_page_blocks(self, page_id: str):
        url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size="
        response = requests.get(url, headers=self.headers)
        return response.json()["results"]

    def _create_page(self, database_id: str, data: dict):
        url = "https://api.notion.com/v1/pages"
        payload = {'parent': {'database_id': database_id}, 'properties': data}
        response = requests.post(url, headers=self.headers, json=payload)
        return response

    def create_person(
            self,
            name: str,
            papers: List[str]=[],
            affiliations: List[str]=[],
            website: str=None):
        # Skip if person already exists in the database
        name = name[:self.cfg.max_text_length]
        if len(self.get_people(name_equals=name)) > 0:
            print(f"ℹ️  Person '{name}' already exists")
            return

        data = {
            self.cfg.person_keys['name']: {'title': [
                {'text': {'content': name}}]}}

        # Papers
        paper_ids = []
        for paper in papers:
            item = self.get_papers(name_equals=paper)
            if len(item) == 0:
                self.create_paper(paper)
                item = self.get_papers(name_equals=paper)
            paper_ids.append(item[0]['id'])
        data[self.cfg.person_keys['papers']] = {
            'relation': [{'id': x} for x in paper_ids]}

        # Affiliations
        affiliation_ids = []
        for affiliation in affiliations:
            item = self.get_affiliations(name_equals=affiliation)
            if len(item) == 0:
                self.create_affiliation(affiliation)
                item = self.get_affiliations(name_equals=affiliation)
            affiliation_ids.append(item[0]['id'])
        data[self.cfg.person_keys['affiliations']] = {
            'relation': [{'id': x} for x in affiliation_ids]}

        # Website
        if website is not None and website != '':
            data[self.cfg.person_keys['website']] = {
                'url': website[:self.cfg.max_text_length]}

        return self._create_page(self.cfg.people_db_id, data)

    def create_paper(
            self,
            name: str,
            authors: List[str]=[],
            topics: List[str]=[],
            to_read: bool=True,
            abstract: str=None,
            url: str=None,
            year: str=None,
            venue: str=None):

        # Skip if paper already exists in the database
        name = name[:self.cfg.max_text_length]
        if len(self.get_papers(name_equals=name)) > 0:
            print(f"ℹ️  Paper '{name}' already exists")
            return

        data = {
            self.cfg.paper_keys['name']: {'title': [
                {'text': {'content': name}}]}}

        # Authors
        author_ids = []
        for author in authors:
            author = author[:self.cfg.max_text_length]
            item = self.get_people(name_equals=author)
            if len(item) == 0:
                self.create_person(author)
                item = self.get_people(name_equals=author)
            author_ids.append(item[0]['id'])
        data[self.cfg.paper_keys['authors']] = {
            'relation': [{'id': x} for x in author_ids]}

        # Topic
        topic_ids = []
        for topic in topics:
            topic = topic[:self.cfg.max_text_length]
            item = self.get_topics(name_equals=topic)
            if len(item) == 0:
                self.create_topic(topic)
                item = self.get_topics(name_equals=topic)
            topic_ids.append(item[0]['id'])
        data[self.cfg.paper_keys['topics']] = {
            'relation': [{'id': x} for x in topic_ids]}

        # Read status
        data[self.cfg.paper_keys['to_read']] = {
            'status': {'name': 'Not started' if to_read else 'Done'}}

        # Abstract
        if abstract is not None:
            # Remove any line breaks
            abstract = ' '.join(abstract.split('\n')).replace('- ', '')
            data[self.cfg.paper_keys['abstract']] = {
                'rich_text': [
                    {'text': {'content': abstract[:self.cfg.max_text_length]}}]}

        # URL
        if url is not None and url != '':
            data[self.cfg.paper_keys['url']] = {
                'url': url[:self.cfg.max_text_length]}

        # Year
        if year is not None:
            data[self.cfg.paper_keys['year']] = {'number': year}

        # Venue
        if venue is not None:
            venue = venue[:self.cfg.max_text_length]
            item = self.get_venues(name_equals=venue)
            if len(item) == 0:
                self.create_venue(venue)
                item = self.get_venues(name_equals=venue)
            venue_id = item[0]['id']
            data[self.cfg.paper_keys['venue']] = {
                'relation': [{'id': venue_id}]}

        return self._create_page(self.cfg.papers_db_id, data)

    def create_affiliation(self, name: str):
        # Skip if affiliation already exists in the database
        name = name[:self.cfg.max_text_length]
        if len(self.get_affiliations(name_equals=name)) > 0:
            print(f"ℹ️  Affiliation '{name}' already exists")
            return

        # Prepare the Notion API json
        data = {
            self.cfg.affiliation_keys['name']: {
                'title': [{'text': {'content': name}}]}}

        return self._create_page(self.cfg.affiliations_db_id, data)

    def create_venue(self, name: str):
        # Skip if venue already exists in the database
        name = name[:self.cfg.max_text_length]
        if len(self.get_venues(name_equals=name)) > 0:
            print(f"ℹ️  Venue '{name}' already exists")
            return

        # Prepare the Notion API json
        data = {
            self.cfg.venue_keys['name']: {
                'title': [{'text': {'content': name}}]}}

        return self._create_page(self.cfg.venues_db_id, data)

    def create_topic(self, name: str):
        # Skip if venue already exists in the database
        name = name[:self.cfg.max_text_length]
        if len(self.get_topics(name_equals=name)) > 0:
            print(f"ℹ️  Topic '{name}' already exists")
            return

        # Prepare the Notion API json
        data = {
            self.cfg.venue_keys['name']: {
                'title': [{'text': {'content': name}}]}}

        return self._create_page(self.cfg.topics_db_id, data)

    def append_page_blocks(self, page_id: str, text: str):
        # Convert input HTML text to Notion API json
        html_text = mistletoe.markdown(text)
        parser = HtmlParser()
        parser.parse(html_text)
        notion_text = [x.dict() for x in parser.content]

        # The Notion API only supports a limited depth for nested items
        # This can cause errors if we have overly-deep bullet lists, for
        # instance. So we flatten all the text beyond a certain depth
        notion_text = self._flatten_max_depth_children(
            notion_text, max_depth=2, marker='•')

        # Append text to page blocks
        url = f"https://api.notion.com/v1/blocks/{page_id}/children"
        payload = {'children': notion_text}
        response = requests.patch(url, json=payload, headers=self.headers)
        return response

    def _update_page(self, page_id: str, data: dict):
        url = f"https://api.notion.com/v1/pages/{page_id}"
        payload = {"properties": data}
        response = requests.patch(url, json=payload, headers=self.headers)
        return response

    def _flatten_block(
            self,
            block: Dict,
            marker: str='•',
            depth: int=1):
        text = ' '.join(
            [x['text']['content'] for x in block[block['type']]['rich_text']])

        if not block['has_children']:
            return text

        text += " ( "

        for child in block[block['type']]['children']:
            flat_child = self._flatten_block(
                child, marker=marker, depth=depth + 1)
            text += f" {marker * depth} {flat_child}"

        text += " ) "

        return text

    def _flatten_children(
            self,
            block: Dict,
            marker: str='•',
            depth: int=1):
        if not block['has_children']:
            return block

        # Recursively flatten and wrap the content of descendent blocks
        text = " ( "
        for child in block[block['type']]['children']:
            flat_child = self._flatten_block(
                child, marker=marker, depth=depth + 1)
            text += f" {marker * depth} {flat_child}"
        text += " ) "

        # Create a new text block containing the flattened children text
        block[block['type']]['rich_text'].append(
            {'type': 'text', 'text': {'content': text}})
        block['has_children'] = False
        del block[block['type']]['children']

        return block

    def _flatten_max_depth_children(
            self,
            blocks: List[Dict],
            depth: int=0,
            max_depth: int=2,
            marker: str='•'):
        for i, block in enumerate(blocks):
            if not block['has_children']:
                continue

            if depth >= max_depth:
                blocks[i] = self._flatten_children(
                    block, marker=marker)
                continue

            self._flatten_max_depth_children(
                block[block['type']]['children'], depth=depth + 1,
                max_depth=max_depth, marker=marker)

        return blocks

    def __repr__(self):
        info = [
            f"{key}={len(getattr(self, key))}"
            for key in ['papers', 'people', 'affiliations', 'venues']]
        return f"{self.__class__.__name__}({', '.join(info)})"
