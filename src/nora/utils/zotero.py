# Fields used from the json format returned by the Zotero API. The order
# in which the below fields are declared matters. When parsing metadata
# returned from a Zotero library or using the Zotero translation server,
# these fields will be resolved in order, to search for information of
# interest for populating our Notion databases. See the official
# documentation for the recommended/expected usage of each field:
# https://www.zotero.org/support/kb/item_types_and_fields

ZOTERO_SUPPORTED_TYPES = [
    'blogPost'
    'book',
    'bookSection',
    'conferencePaper',
    'encyclopediaArticle',
    'journalArticle',
    'magazineArticle',
    'manuscript',
    'newspaperArticle',
    'patent',
    'presentation',
    'report',
    'thesis',
    'webpage']

ZOTERO_VENUE_FIELDS = [
    'bookTitle',
    'proceedingsTitle',
    'conferenceName',
    'meetingName',
    'publicationTitle',
    'journalAbbreviation',
    'publisher',
    'university',
    'institution',
    'archiveLocation',
    'websiteTitle',
    'libraryCatalog',
    'place']

ZOTERO_DATE_FIELDS = [
    'date',
    'issueDate',
    'publicationDate',
    'filingDate',
    'submittedDate',
    'eventDate',
    'originalDate',
    'accessed',
    'accessDate']
