import numpy
import pytest
import sqlite3

from src.sqlite import SqliteDB
from src.database_data_handlers import DatabaseManager
from src.exceptions import TitleTooLongError

database_name = "test_db.db"

@pytest.fixture
def setup_test_db():
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

  yield conn
  
  conn.close()

@pytest.fixture
def database_manager():
  return DatabaseManager(database_name)

@pytest.mark.usefixtures("setup_test_db")
def test_save_data_to_db_populates_the_db_tables(database_manager):
  '''
  Given a set of data containing a title, timestamp and content
  When we pass this data to save_data_to_db
  Then we expect to have this data set on their respective columns and rows
  '''

  title = "document title B"
  timestamp = "2023-03-22 14:20:00.00"
  content = "document text content (revision 1)"

  # Adding data to test_db database
  database_manager.save_data_to_db(title, timestamp, content)

  # Getting data store in test_db

  conn = sqlite3.connect(database_name)
  cursor = conn.cursor()

  rows_query = cursor.execute("""
    SELECT title, creation_timestamp, document_content FROM documents_metadata
    INNER JOIN documents_data ON documents_data.document_id = documents_metadata.document_id
    INNER JOIN titles ON documents_metadata.title_id = titles.title_id
    WHERE
      documents_metadata.title_id = ( SELECT title_id FROM titles WHERE title = ? )
    """, ( title, )
  )

  rows = rows_query.fetchall()
  title_row = list(numpy.concatenate(rows))

  assert title_row == ['document title B', '2023-03-22 14:20:00.00', 'document text content (revision 1)']

@pytest.mark.usefixtures("setup_test_db")
def test_save_data_to_db_raises_title_too_long_error(database_manager):
  '''
  Given a set of data containing a title, timestamp and content
  Where the title is longer than 50 chars
  When we pass this data to save_data_to_db
  Then we expect to raise TitleTooLongError exception
  '''

  document_title = "This is a really really really unnecessarily long title"
  creation_timestamp = "2023-03-22 14:00:00.00"
  document_content_data = "document text content"

  with pytest.raises(TitleTooLongError):
    database_manager.save_data_to_db(document_title, creation_timestamp, document_content_data)
