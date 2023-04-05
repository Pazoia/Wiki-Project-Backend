import numpy
import sqlite3

from src.database_data_handlers import DatabaseManager
from src.exceptions import (
  NoChangesDetected,
  NoDataInDatabase,
  NoDocumentCreatedAtTimestamp,
  TitleNotFound
)

class DocumentStoreActions:
  def __init__(self, database_name = "wiki_documents_db.db"):
    self.database_name = database_name
    self.data_handler = DatabaseManager(database_name)

  def db_connection(self):
    try:
      conn = sqlite3.connect(self.database_name)
      cursor = conn.cursor()
    except sqlite3.Error as error:
      print(error)

    return conn, cursor
  
  def get_titles(self):

    [conn, cursor] = self.db_connection()

    rows_query = cursor.execute("SELECT title FROM titles")
    rows = rows_query.fetchall()

    if len(rows) == 0:
      raise NoDataInDatabase(f"Database has no data in it, make sure to load some data into {self.database_name} before trying to retrieve data from it.")
    
    titles_list = list(numpy.concatenate(rows))

    conn.close()
    return titles_list
  
  def get_documents(self, title):
    
    [conn, cursor] = self.db_connection()

    rows_query = cursor.execute("""
      SELECT title, creation_timestamp, document_content FROM documents_metadata
      INNER JOIN documents_data ON documents_data.document_id = documents_metadata.document_id
      INNER JOIN titles ON documents_metadata.title_id = titles.title_id
      WHERE
        documents_metadata.title_id = ( SELECT title_id FROM titles WHERE title = ? )
      """, ( title, )
    )

    documents_list = rows_query.fetchall()
    
    if len(documents_list) == 0:
      raise TitleNotFound(f"Title: '{title}' not found, please check the provided title is correct. Please note that the tile is case sensitive and it needs to match exactly the title stored in the database.")
    
    conn.close()
    return documents_list

  def get_document_as_it_was_at_a_given_timestamp(self, title, timestamp):
    
    [conn, cursor] = self.db_connection()

    rows_query = cursor.execute("""
      SELECT title, creation_timestamp, document_content FROM documents_metadata
      INNER JOIN documents_data ON documents_data.document_id = documents_metadata.document_id
      INNER JOIN titles ON documents_metadata.title_id = titles.title_id
      WHERE
        documents_metadata.title_id = ( SELECT title_id FROM titles WHERE title = ? )
      AND
        documents_metadata.creation_timestamp <= ?
      ORDER BY documents_metadata.creation_timestamp DESC LIMIT 1
      """, ( title, timestamp, )
    )

    rows = rows_query.fetchall()

    if len(rows) == 0:
      if title in self.get_titles():
        # Getting the earliest revision available for title
        rows_query = cursor.execute("""
          SELECT title, MIN(creation_timestamp), document_content FROM documents_metadata
          INNER JOIN documents_data ON documents_data.document_id = documents_metadata.document_id
          INNER JOIN titles ON documents_metadata.title_id = titles.title_id
          WHERE
            documents_metadata.title_id = ( SELECT title_id FROM titles WHERE title = ? )
          """, ( title, )
        )
        rows = rows_query.fetchall()

        raise NoDocumentCreatedAtTimestamp(f"There are no document revisions created for title '{title}' before timestamp: {timestamp}. The earlier revision for this title was created at timestamp: {rows[0][1]}")
      else:
        raise TitleNotFound(f"Title: '{title}' not found, please check the provided title is correct. Please note that the tile is case sensitive and it needs to match exactly the title stored in the database.")
      
    document_revision_at_a_given_timestamp = list(numpy.concatenate(rows))

    conn.close()
    return document_revision_at_a_given_timestamp

  def get_latest_document_revision(self, title):
    
    [conn, cursor] = self.db_connection()

    rows_query = cursor.execute("""
      SELECT title, MAX(creation_timestamp), document_content FROM documents_metadata
      INNER JOIN documents_data ON documents_data.document_id = documents_metadata.document_id
      INNER JOIN titles ON documents_metadata.title_id = titles.title_id
      WHERE
        documents_metadata.title_id = ( SELECT title_id FROM titles WHERE title = ? )
      """, ( title, )
    )

    rows = rows_query.fetchall()
    if rows[0][1] == None:
      raise TitleNotFound(f"Title: '{title}' not found, please check the provided title is correct. Please note that the tile is case sensitive and it needs to match exactly the title stored in the database.")

    latest_document_revision = list(numpy.concatenate(rows))

    conn.close()
    return latest_document_revision
  
  def post_new_document_revision(self, title, timestamp, new_content):

    titles_list = self.get_titles()
    old_content = self.get_latest_document_revision(title)

    if old_content[2] == new_content:
      raise NoChangesDetected(f"No changes detected in new content for title: {title}")
    if title not in titles_list:
      raise TitleNotFound(f"Title: '{title}' not found, please check the provided title is correct. Please note that the tile is case sensitive and it needs to match exactly the title stored in the database.")
    else:
      self.data_handler.save_data_to_db(title, timestamp, new_content)
      return f"New document saved to {title}"
