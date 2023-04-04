# Database Design

## This is how I plan to structure the design of the database for storing wiki Docs data.

### database name:

**wiki_documents_db**

### database tables:

> **_titles_**  
> In this table we will store all the titles

| title_ID | title                         |
| :------- | :---------------------------- |
| UUID     | Immutable Title, max 50 chars |

> **_documents_metatada_**  
> In this table we will store entries with the details of each document corresponding to a `title`

| document_id                    | creation_timestamp                           | title_id                                      |
| :----------------------------- | :------------------------------------------- | :-------------------------------------------- |
| UUID for this document version | Timestamp of document creation date and time | UUID from corresponding title on titles table |

> **_documents_data_**  
> In this table we will store the entries of the text content for the documents in the `documents` table

| document_id                                        | document_content         |
| :------------------------------------------------- | :----------------------- |
| UUID from respective document on list_of_documents | text within the document |
