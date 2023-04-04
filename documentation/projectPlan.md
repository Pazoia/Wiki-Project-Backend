# Project Planning

## This is how I plan to approach this project

### - Setup a skeleton folder structure for project

### - Install required dependencies and save them to requirements file

### - Create dummy docs with text to load data into DB.

### - Create a simple flask server that I can update with the API endpoints requested

### - Create SQLite wiki_documents_db database.

### - Add logic to create tables in DB following the databaseDesignPlan.

### - Load the data from dummy docs into respective tables and rows in DB

### - Create endpoint for:

- GET /documents
- This should return a list of available titles.

### - Create endpoint for:

- GET /documents/title
- This should return a list of available revisions for a document.

### - Create endpoint for:

- GET /documents/title/timestamp
- This should return the document as it was at that timestamp.

### - Create endpoint for:

- GET /documents/title/latest
- This should return the current latest version of the document.

### - Create endpoint for:

- POST /documents/title
- This allows users to post a new revision of a document.
  It should receive JSON in the form: {content: ‘new content...’}.
