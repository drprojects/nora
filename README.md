<div align="center">

# NoRA - Notion Research Assistant 

[![python](https://img.shields.io/badge/-Python-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![node.js](https://img.shields.io/badge/Node.js-43853D?logo=node.js&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/ashleve/lightning-hydra-template#license)

A Notion template to help you keep track of the papers you read 📜, their authors 👤, 
your notes 📝, and more 🔥

**_If you ❤️ or simply use this project, don't forget to give the repository a ⭐,
it means a lot to us !_**
</div>

<br>

## 📌  Introduction

This project was built as a [Notion](https://www.notion.so)-based alternative to 
reference management software such as Zotero and Mendeley.

It is composed of the **NoRA Notion template** for you to build on top of, as 
well as **NoRA-Tools** to programmatically:
- 🔥 upload papers to your NoRA library as easily as with 
[Zotero Connector](https://www.zotero.org/download/connectors) from a simple URL or an identifier
- 🔥 move all your already-existing Zotero library to NoRA

### 🧪  NoRA template

The NoRA Notion template provides you with a structure of interconnected databases to 
keep track of your research papers and notes.
More specifically, the template contains the following databases:
- `🏗️ Projects`
- `📜 Papers`
- `👤 People`
- `🏢 Affiliations`
- `🤹 Conferences & journals`
- `🧲 Key topics`

The inner workings of the template are quite straightforward, the best way to 
get familiar with it is probably to play with it 😉 !

### 🛠  NoRA-Tools

The NoRA-Tools provide functionalities to programmatically upload data to your 
NoRA template. The main functionalities are:

- uploading a paper and associated metadata to NoRA from a URL or 
from an identifier (DOI, ISBN, PMID, arXiv ID), exactly like with 
[Zotero Connector](https://www.zotero.org/download/connectors)
- uploading your whole Zotero library to NoRA

<br>

## 🧱  Installation

### Requirements
- [Python](https://www.python.org/downloads) ≥ 3.9  
- [pip](https://pip.pypa.io/en/stable/installation)
- [Node.js](https://nodejs.org/en/download) ≥ 18 and ≤ 20  
- [Notion](https://www.notion.com) account with API credentials
- (optional) [Zotero](https://www.zotero.org) account with API credentials

> **Note**: We have experienced issues with too-recent `node.js` 
> versions such as `node 23` so we recommend making sure you use 
> `node 20` for now. You can check your version by running `node -v`.

### Installing the template in Notion

Simply duplicate the [NoRA template](https://silent-switch-780.notion.site/Template-research-library-286d3393a7e845c6a689a5c693790987) to your personal Notion account.

> **Note**: You can freely modify or extend the NoRA template. However, keep in 
> mind that if you want to use NoRA-Tools after modifying some sensitive page 
> fields, you may need to adjust your 
> [Notion configuration](###getting-your-notion-api-keys) accordingly.

### Getting your Notion API keys

Next, you will need to prepare some private keys needed to upload data 
to your NoRA.
To this end, do the following:
- [Create an integration](https://developers.notion.com/docs/create-a-notion-integration) for your NoRA workspace
- [Recover your **API secret token**](https://developers.notion.com/docs/create-a-notion-integration#get-your-api-secret)
- For each database in the NoRA template (i.e. Papers, People, Affiliations, Venues, Topics):
  - [Give your integration permission to access this database](https://developers.notion.com/docs/create-a-notion-integration#give-your-integration-page-permissions)
  - Recover your **database ID**. For this, open the database page **in a browser**. The
database ID is a 32-alphanumeric-character that can be recovered from the URL of the page:
`https://www.notion.so/this_is_your_32_character_database_id?v=you_can_ignore_the_rest`

Once you have recovered your **API secret token** and the **database IDs**, 
you should have something like this:

````yaml
notion:
    token: your_api_secret_token
    papers_db_id: your_papers_database_id
    people_db_id: your_people_database_id
    affiliations_db_id: your_affiliations_database_id
    venues_db_id: your_venues_database_id
    topics_db_id: your_topics_database_id
````
Keep these safe somewhere, we will need these in a bit!

### Getting your Zotero API keys (optional)

If you intend to move your whole Zotero library to Notion, you will need to
get some private keys to download your library.
To this end, you will need to:
- Get your Zotero **library ID** by checking the UserID in your [profile settings](https://www.zotero.org/settings/keys)
- Create a Zotero **API key** in your [profile settings](https://www.zotero.org/settings/keys)

You should then have something like this:

````yaml
zotero:
    library_id: your_library_id
    api_token: your_api_key
````

Keep these safe somewhere, we will need these in a bit!

### Installing NoRA-Tools on your machine
Open a terminal and run
```bash
pip install git+https://github.com/drprojects/nora.git
```

then configure you API keys
```bash
nora configure
```
this will prompt you to pass your secret keys, which will be saved in 
`~/.nora/config.yaml`.

<details>
<summary><b>
⚠️ Are you using a `.netrc` file with a `default` configuration?</b></summary>

If you are using a `~/.netrc` file to keep track of your passwords locally, 
and have declared a `default` account among your configurations, the `requests`
library will crash when trying to connect to Notion. Please remove your 
`default` account and all should be fine 😉

</details>

### Uninstalling NoRA-Tools from your machine
Open a terminal and run
```bash
pip uninstall nora
```

<br>

## ⚡  Using NoRA-Tools

### Uploading a paper to NoRA

NoRA-Tools mimics the behavior of the 
[Zotero Connector](https://www.zotero.org/download/connectors), which 
has two mechanisms for uploading a paper.

From a URL:

```bash
nora url https://arxiv.org/abs/2204.07548
```

From an identifier (DOI, ISBN, PMID, arXiv ID):

```bash
nora id 2204.07548
```

### Uploading your entire Zotero library to NoRA

```bash
nora zotero.upload=True
```

<br>

## 👩‍💻  NoRA for developers

If you want to extend NoRA-Tools to your need, you can install from source:

```bash
# Get the source code
git clone --recurse-submodules https://github.com/drprojects/nora

# Install the python dependencies
cd nora
pip install -e .

# Install the node.js server
cd src/nora/translation_server
npm install
cd ../..
```

<details>
<summary><b>Modifying field names in NoRA?️</b></summary>

By default, NoRA-Tools expect the attribute fields (e.g. column names in Notion)
of your papers, people, etc. to have specific values. If you want to adjust 
those, you will also need to adjust the
[configs/config.yaml](src/nora/configs/config.yaml)
file:

````yaml
# If you happen to modify your field names in Notion, update the
# following database-specific keys
person_keys:
    name: 'Name'
    affiliations: '🏢 Affiliations'
    papers: '📜 Papers'
    website: 'Website'

paper_keys:
    name: 'Name'
    authors: '👤 Authors'
    abstract:  'Abstract'
    topics: '🧲 Key topics'
    url: 'URL'
    to_read: 'Reading status'
    year: 'Year'
    venue:  '🤹 Venue'

affiliation_keys:
    name: 'Name'

venue_keys:
    name: 'Name'
````

</details>

<details>
<summary><b>
Adding your own 🤹 Conferences & journals?</b></summary>

By default, when parsing a paper from a remote database, NoRA-Tools will try to 
figure out which `🤹 Conferences & journals` to place it under. However, one 
can hardly account for all possible conference and journal names, nor for all 
the slight formatting differences used to describe how a paper was published. 
Yet, we attempt to group the most frequent ones using a predefined `VENUES` 
dictionary in `src/utils/venues.py`.

If many papers from your library are from a conference or journal absent from 
this dictionary, and you would like them to be grouped under the same 
`🤹 Conferences & journals` item, you can simply append your own entries in 
`VENUES`, using the following format:

````python
lowercase_match_to_search_for_in_remote_metadata: 'shorthand_under_which_to_group'
````

</details>

<details>
<summary><b>
Conflicts with `.netrc`</b></summary>

If you are using a `~/.netrc` file to keep track of your passwords locally, 
and have declared a `default` account among your configurations, the `requests`
library will crash when trying to connect to Notion. Please remove your 
`default` account and all should be fine 😉

</details>

<details>
<summary><b>
Ignoring Zotero collections when migrating from Zotero to Notion</b></summary>

By default, the `collections` (e.g. folders) in your Zotero library will be used to 
populate the `Key Topics` field of your papers in NoRA.
If you want to exclude some of your collections from this behavior, your can list 
them in the [configs/zotero/default.yaml](src/nora/configs/zotero/default.yaml) file:

````yaml
ignored_collections: ['collection name 1', 'collection name 2']
````
</details>

<br>

## License

NoRA is released under the MIT License.

```
MIT License

Copyright (c) 2023-2025 Damien Robert

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
