<div align="center">

# NoRA - Notion Research Assistant 

[![python](https://img.shields.io/badge/-Python-blue?logo=python&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![hydra](https://img.shields.io/badge/Config-Hydra_1.2-89b8cd)](https://hydra.cc/)
[![license](https://img.shields.io/badge/License-MIT-green.svg?labelColor=gray)](https://github.com/ashleve/lightning-hydra-template#license)

A Notion template to help you keep track of the papers you read 📜, their authors 👤, 
your notes 📝, and more 🔥

</div>

<br>

## 📌  Introduction

This project was built as a [Notion](https://www.notion.so)-based alternative to 
reference management softwares such as Zotero and Mendeley.

It is composed of the **NoRA Notion template** for you to build on top of, as 
well as **NoRA-Tools** to programmatically:
- 🔥 upload papers to your NORA library as easily as with 
[Zotero Connector](https://www.zotero.org/download/connectors) from a simple URL or an identifier
- 🔥 move all your already-existing Zotero library to NoRA

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
NoRA template. The main functionalities are:

- uploading a paper and associated metadata to NoRA from a URL or 
from an identifier (DOI, ISBN, PMID, arXiv ID), exactly like with 
[Zotero Connector](https://www.zotero.org/download/connectors)
- uploading your whole Zotero library to NoRA 

You can freely modify or extend the NoRA template. However, keep in mind that if 
you want to use NoRA-Tools after modifying some sensitive page fields, you may 
need to adjust your [Notion configuration](###notion-configuration) accordingly.

<br>

## 🧱  Installation

### Requirements
- `npm` installed
- `conda` installed
- Notion account

### Installing the template in Notion

Simply duplicate the [NoRA template](https://silent-switch-780.notion.site/Template-research-library-286d3393a7e845c6a689a5c693790987) to your personal Notion account.

### Installing NoRA-Tools on your machine

```bash
# clone project
git clone --recurse-submodules git@github.com:drprojects/nora.git
cd nora

# create a 'nora' conda environment with required dependencies
conda env create -f nora.yml

# install the npm server
cd src/translation_server
npm install
cd ../..
```


<details>
<summary><b>Setting up NoRA-Tools for simpler bash commands (optional, unix machines only)</b></summary>

As you will see below, executing NoRA-Tools requires activating a conda 
environment and calling a python script following a specific syntax. 
For more convenience, it is also possible to configure NoRA to be called using a 
simpler bash syntax. To this end, you need to do two things.

First, indicate the path to your conda installation directory in the [`nora`](nora) 
bash script:
```bash
CONDA_DIR=/path/to/your/conda/installation/directory
```

Next, you will need to add the `nora/` project repository to the `$PATH$` environment 
variable of your machine. This way, you will be able to call the [`nora`](nora) 
script from anywhere ! To do this, you typically want to add something like this to your 
`.bashrc`:
```bash
export PATH=/path/to/repository/nora${PATH:+:${PATH}}
```

</details>

### Notion configuration

Next, you will need to configure your NoRA-Tools to connect to your NoRA databases in Notion.
To this end, do the following:
- [Create an integration](https://developers.notion.com/docs/create-a-notion-integration) for your NoRA workspace
- [Recover your **API secret token**](https://developers.notion.com/docs/create-a-notion-integration#get-your-api-secret)
- For each database in the NoRA template (ie Papers, People, Affiliations, Venues, Topics):
  - [Give your integration permission to access this database](https://developers.notion.com/docs/create-a-notion-integration#give-your-integration-page-permissions)
  - Recover your **database ID**. For this, open the database page **in a browser**. The
database ID is a 32-alphanumeric-character that can be recovered from the URL of the page:
`https://www.notion.so/this_is_your_32_character_database_id?v=you_can_ignore_the_rest`

Once you have recovered your **API secret token** and the **database IDs**, you must save 
these in the `configs/notion/default.yaml` file:

````yaml
# Adapt to your own Notion library.
# See https://developers.notion.com/docs/create-a-notion-integration
token: "your_api_secret_token"
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


### Zotero configuration (optional)

If you intend to move your whole Zotero library to Notion, you will need to configure 
your NoRA-Tools accordingly.
To this end, you will need to:
- Get your Zotero **library ID** by checking the UserID in your [profile settings](https://www.zotero.org/settings/keys)
- Create a Zotero **API key** in your [profile settings](https://www.zotero.org/settings/keys)

You can then save your Zotero **library ID** and **API key** in the 
`configs/zotero/default.yaml` file:

````yaml
# Adapt to your own Zotero library
library_id: 'your_library_id'
api_token: 'your_api_key'
````

By default, the `collections` (eg folders) in your Zotero library will be used to 
populate the `Key Topics` field of your papers in NoRA.
If you want to exclude some of your collections from this behavior, your can list 
them in:

````yaml
ignored_collections: ['collection name 1', 'collection name 2']
````

### Proxy configuration (optional)

If your machine has a proxy, you will need to configure your NoRA-Tools to use it.
To this end, specify your `$HTTP_PROXY` and `$HTTPS_PROXY` in the 
`configs/proxy/default.yaml` file:

````yaml
http_proxy: 'your_http_proxy'
https_proxy: 'your_https_proxy'
````

<br>

## ⚡  Using NoRA-Tools

### Uploading a paper to NoRA

NoRA-Tools mimics the behavior of the 
[Zotero Connector](https://www.zotero.org/download/connectors), which 
has two mechanisms for uploading a paper.

From a URL:

```bash
# In your activated nora conda environment
python nora.py url=https://arxiv.org/abs/2204.07548
```

<details>
<summary>If you set up NoRA for simpler unix commands</summary>

```bash
nora url=https://arxiv.org/abs/2204.07548
```

</details>

From an identifier (DOI, ISBN, PMID, arXiv ID):

```bash
# In your activated nora conda environment
python nora.py "id='2204.07548'"
```

<details>
<summary>If you set up NoRA for simpler unix commands</summary>

```bash
nora "id='2204.07548'"
```

</details>

> **Note**: we use [hydra](https://hydra.cc) for parsing shell commands and 
> recommend using quotes as shown above when querying `id=...`. This is to
> avoid some potential trailing zeros to be ignored when parsing your shell 
> arguments. For more details on this, see the 
> [hydra documentation](https://hydra.cc/docs/1.2/advanced/override_grammar/basic/#quoted-values).

> **Note**: NoRA uses `psutil.net_connections()` which requires sudo 
> privileges on macOS. Unfortunately, there is no workaround this, you will
> need to run `nora` as sudo on macOS.

### Uploading your entire Zotero library to NoRA

```bash
python nora.py zotero.upload=True
```

<details>
<summary>If you set up NoRA for simpler unix commands</summary>

```bash
nora zotero.upload=True
```

</details>

<br>

## License

NoRA is released under the MIT License.

```
MIT License

Copyright (c) 2023-2024 Damien Robert

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
