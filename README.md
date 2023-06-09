<div align="center">

# NoRA - Notion Research Assistant 

[![python](https://img.shields.io/badge/-Python-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![hydra](https://img.shields.io/badge/Config-Hydra_1.2-89b8cd)](https://hydra.cc/)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/ashleve/lightning-hydra-template#license)

A Notion template to help you keep track of the papers you read, their authors, 
your notes and more 🚀⚡🔥

</div>

<br>

## 📌  Introduction

This project was built as a [Notion](https://www.notion.so)-based alternative to 
reference management softwares such as Zotero and Mendeley.

It is composed of the **NoRA Notion template** for you to build on top of, as 
well as **NoRA-Tools** to programmatically:
- 🔥 upload an arxiv paper to your NoRA library from its ID, URL or title
- 🔥 move all your Zotero library to your NoRA library

### 🧪  NoRA template

The NoRA template provides you with a structure of interconnected databases to 
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
NoRA template. For now, the two main functionalities are uploading your whole 
Zotero library to NoRA and uploading an arxiv paper (and associated metadata) 
to NoRA.

You can freely modify or extend the NoRA template. However, keep in mind that if 
you want to use NoRA-Tools after modifying some sensitive page fields, you will 
need to adjust your [Notion configuration](###notion-configuration) accordingly.

<br>

## 🧱  Installation

### Installing the template

Simply duplicate the [NoRA template](https://silent-switch-780.notion.site/Template-research-library-286d3393a7e845c6a689a5c693790987) to your personal Notion account.

### Installing NoRA tools

First, install the NoRA-Tools locally on your machine.

```bash
# clone project
git clone git@github.com:drprojects/nora.git
cd nora

# create a 'nora' conda environment with required dependencies
conda env create -f nora.yml
```

### Notion configuration

Next, you will need to configure your NoRA-Tools to connect to your NoRA databases in Notion.
To this end, follow the official guide to [Create a Notion Integration](https://developers.notion.com/docs/create-a-notion-integration).
Following all steps in this page you will:
- Create an integration and get a **Token**
- For each database in the NoRA template:
  - Share the database with your integration
  - Save the **database ID**

You can then save the **Token** and the **database IDs** in the `configs/notion/default.yaml` file:

````yaml
# Adapt to your own Notion library.
# See https://developers.notion.com/docs/create-a-notion-integration
token: "your_integration_token"
papers_db_id: "your_papers_database_id"
people_db_id: "your_people_database_id"
affiliations_db_id: "your_affiliations_database_id"
venues_db_id: "your_venues_database_id"
topics_db_id: "your_topics_database_id"
````

<details>
<summary><b>⚠️ Want to modify some field names in NoRA ?️</b></summary>

By default, NoRA-Tools expect the attribute fields (eg column names in Notion) of your papers, people, etc. to have specific values.
If you want to adjust those, you will also need to adjust the `configs/notion/default.yaml` file:

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
⚠️ Want to add your own 🤹 Conferences & journals ?️</b></summary>

By default, when parsing an arxiv paper, NoRA-Tools will try to figure out 
which `🤹 Conferences & journals` to place it under. However, one can hardly 
account for all possible conference and journal names, nor for all the slight 
formatting differences used to describe how a paper was published. Yet, we 
attempt to group the most frequent ones using a predefined `VENUES` dictionary 
in `nora/utils/venues.py`.

If many papers from your library are from a conference or journal absent from 
this dictionary, and you would like them to be grouped under the same 
`🤹 Conferences & journals` item, you can simply append your own entries in 
`VENUES`, using the following format:

````python
'lowercase_match_to_search_for_in_arxiv_metadata': 'shorthand_under_which_to_group'
````

</details>

### Zotero configuration (optional)

If you intend to move your whole Zotero library to Notion, you will need to configure your NoRA-Tools accordingly.
To this end, you will need to:
- Get your Zotero **library ID** by checking the UserID in your [profile settings](https://www.zotero.org/settings/keys)
- Create a Zotero **API key** in your [profile settings](https://www.zotero.org/settings/keys)

You can then save your Zotero **library ID** and **API key** in the `configs/zotero/default.yaml` file:

````yaml
# Adapt to your own Zotero library
library_id: 'your_library_id'
api_token: 'your_api_key'
````

By default, the `collections` (eg folders) in your Zotero library will be used to populate the `Key Topics` field of your papers in NoRA.
If you want to exclude some of your collections from this behavior, your can list them in:

````yaml
ignored_collections: ['collection name 1', 'collection name 2']
````

### Proxy configuration (optional)

If your machine has a proxy, you will need to configure your NoRA-Tools to use it.
To this end, specify your `$HTTP_PROXY` and `$HTTPS_PROXY` in the `configs/proxy/default.yaml` file:

````yaml
http_proxy: 'your_http_proxy'
https_proxy: 'your_https_proxy'
````

<br>

## ⚡  Using NoRA-Tools

### Uploading an arxiv paper to NoRA

From its arxiv ID:

```bash
python nora/arxiv_to_nora.py arxiv.id="'2204.07548'"
```

From its url:

```bash
python nora/arxiv_to_nora.py arxiv.id="https://arxiv.org/abs/2204.07548"
```

From its title:

```bash
python nora/arxiv_to_nora.py arxiv.title="Learning Multi-View Aggregation In the Wild for Large-Scale 3D Semantic Segmentation"
```

### Uploading your entire Zotero library to NoRA

```bash
python nora/zotero_to_nora.py
```

<br>

## License

NoRA is licensed under the MIT License.

```
MIT License

Copyright (c) 2021 ashleve

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
