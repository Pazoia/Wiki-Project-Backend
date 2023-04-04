import pytest
import sqlite3

from src.sqlite import SqliteDB
from src.document_store_actions import DocumentStoreActions
from src.database_data_handlers import DatabaseManager
from src.exceptions import (
  NoDataInDatabase,
  TitleNotFound,
  NoDocumentCreatedAtTimestamp
)

database_name = "test_db.db"

@pytest.fixture
def setup_test_db_with_data():
  # Create test_db file if one doesn't exist yet
  conn = sqlite3.connect(database_name)
  cursor = conn.cursor()

  # Reset the database by deleting all data
  try:
    cursor.execute("DROP TABLE IF EXISTS titles")
    cursor.execute("DROP TABLE IF EXISTS documents_metadata")
    cursor.execute("DROP TABLE IF EXISTS documents_data")
    conn.commit()
  except sqlite3.Error as error:
    print(error)
    conn.rollback()

  # Add tables to test_db
  test_db = SqliteDB(database_name)
  test_db.database_setup()

  # Add data to tables
  data = [
    {
      "document_title": "document title A",
      "creation_timestamp": "2023-03-22 14:00:00.00",
      "document_content": "document text content A"
    },
    {
      "document_title": "document title B",
      "creation_timestamp": "2023-03-22 14:10:00.00",
      "document_content": "document text content (revision 1)"
    },
    {
      "document_title": "document title B",
      "creation_timestamp": "2023-03-22 14:15:00.00",
      "document_content": "document text content (revision 2)"
    }
  ]

  database_manager = DatabaseManager(database_name)
  for document in data:
    document_title = document["document_title"]
    creation_timestamp = document["creation_timestamp"]
    document_content = document["document_content"]

    database_manager.save_data_to_db(document_title, creation_timestamp, document_content)
  
  yield conn
  
  conn.close()

@pytest.fixture
def document_store_actions():
  return DocumentStoreActions(database_name)

def test_get_titles_on_an_empty_database_raises_error(document_store_actions):
  '''
  Given an empty DB
  When we call get_titles on it
  Then we expect to raise NoDataInDatabase exception
  '''

  # Create test_db file if one doesn't exist yet
  conn = sqlite3.connect(database_name)
  cursor = conn.cursor()

  # Reset the database by deleting all data
  try:
    cursor.execute("DROP TABLE IF EXISTS titles")
    cursor.execute("DROP TABLE IF EXISTS documents_metadata")
    cursor.execute("DROP TABLE IF EXISTS documents_data")
    conn.commit()
  except sqlite3.Error as error:
    print(error)
    conn.rollback()

  # Add tables to test_db
  test_db = SqliteDB(database_name)
  test_db.database_setup()

  with pytest.raises(NoDataInDatabase):
    document_store_actions.get_titles()

  conn.close()

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_titles_returns_data_from_db(document_store_actions):
  '''
  Given a database with many titles
  When we call get_titles on it
  Then we expect it to return a list of all available titles
  '''
  
  title_list = document_store_actions.get_titles()

  assert title_list == ['document title A', 'document title B']

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_documents_returns_data_from_db(document_store_actions):
  '''
  Given a database with many document revisions for a title
  When we call get_documents on it
  Then we expect it to return a list of all available revisions
  '''

  title = "document title B"
  document_list = document_store_actions.get_documents(title)

  assert document_list == [
    ('document title B', '2023-03-22 14:10:00.00', 'document text content (revision 1)'),
    ('document title B', '2023-03-22 14:15:00.00', 'document text content (revision 2)')
  ]

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_documents_raises_title_not_found_exception(document_store_actions):
  '''
  Given a database with many document revisions for a title
  When we call get_documents with a title that is not in the DB
  Then we expect it to raise TitleNotFound exception
  '''

  title = "document title C"

  with pytest.raises(TitleNotFound):
    document_store_actions.get_documents(title)

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_document_as_it_was_at_a_given_timestamp_returns_data_from_db(document_store_actions):
  '''
  Given a database with many document revisions for a title
  When we call get_document_as_it_was_at_a_given_timestamp on it
  Then we expect it to return a document revision as it was at the given timestamp
  '''

  title = "document title B"
  timestamp = "2023-03-22 14:14:00.00"
  document_revision = document_store_actions.get_document_as_it_was_at_a_given_timestamp(title, timestamp)

  assert document_revision == [
    'document title B', '2023-03-22 14:10:00.00', 'document text content (revision 1)'
  ]

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_document_as_it_was_at_a_given_timestamp_raises_no_title_exception(document_store_actions):
  '''
  Given a database with many document revisions for a title
  When we call get_document_as_it_was_at_a_given_timestamp on it
  WITH a title that does not exist in the db
  Then we expect it to raise TitleNotFound exception
  '''

  title = "document title C"
  timestamp = "2023-03-22 14:14:00.00"

  with pytest.raises(TitleNotFound):
    document_store_actions.get_document_as_it_was_at_a_given_timestamp(title, timestamp)

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_document_as_it_was_at_a_given_timestamp_raises_no_revision_exception(document_store_actions):
  '''
  Given a database with many document revisions for a title
  When we call get_document_as_it_was_at_a_given_timestamp on it with a timestamp
  AND there are no revision for the timestamp
  Then we expect it to raise NoDocumentCreatedAtTimestamp exception
  '''

  title = "document title B"
  timestamp = "2023-02-22 14:14:00.00"

  with pytest.raises(NoDocumentCreatedAtTimestamp):
    document_store_actions.get_document_as_it_was_at_a_given_timestamp(title, timestamp)

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_latest_document_revision_returns_data_from_db(document_store_actions):
  '''
  Given a database with many document revisions for a title
  When we call get_latest_document_revision on it
  Then we expect it to return a the most recent document revision available
  '''

  title = "document title B"
  latest_document_revision = document_store_actions.get_latest_document_revision(title)

  assert latest_document_revision == [
    'document title B', '2023-03-22 14:15:00.00', 'document text content (revision 2)'
  ]

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_get_latest_document_revision_raises_no_title_exception(document_store_actions):
  '''
  Given a database with many document revisions for a title
  When we call get_latest_document_revision on it with a title that is not in the DB
  Then we expect it to raise TitleNotFound exception
  '''

  title = "document title C"

  with pytest.raises(TitleNotFound):
    document_store_actions.get_latest_document_revision(title)

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_post_new_document_revision_adds_data_to_db(document_store_actions):
  '''
  Given a database with at least a title
  When we call post_new_document_revision on it with a valid title
  Then we expect it to add a new document revision to the title
  '''

  title = "document title B"
  timestamp = "2023-03-22 14:20:00.00"
  content = "document text content (revision 3)"

  # Adding new revision to title
  document_store_actions.post_new_document_revision(title, timestamp, content)

  # Getting all document revision for title: 'document title B'
  document_revisions_list = document_store_actions.get_documents(title)

  assert document_revisions_list == [
    ('document title B', '2023-03-22 14:10:00.00', 'document text content (revision 1)'),
    ('document title B', '2023-03-22 14:15:00.00', 'document text content (revision 2)'),
    ('document title B', '2023-03-22 14:20:00.00', 'document text content (revision 3)')
  ]

@pytest.mark.usefixtures("setup_test_db_with_data")
def test_post_new_document_revision_returns_no_title_exception(document_store_actions):
  '''
  Given a database with at least a title
  When we call post_new_document_revision on it with a title not available in DB
  Then we expect it to return TitleNotFound exception
  '''

  title = "document title C"
  timestamp = "2023-03-22 14:20:00.00"
  content = "document text content (revision 3)"

  with pytest.raises(TitleNotFound):
    # Adding new revision to title
    document_store_actions.post_new_document_revision(title, timestamp, content)
