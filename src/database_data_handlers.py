import sqlite3
import uuid

from src.helper_functions import get_data_from_file
from src.exceptions import TitleTooLongError

class DatabaseManager:
  def __init__(self, database_name = "wiki_documents_db.db"):
    self.database_name = database_name

  def db_connection(self):
    try:
      conn = sqlite3.connect(self.database_name)
      cursor = conn.cursor()
    except sqlite3.Error as error:
      print(error)

    return conn, cursor
  
  def save_data_to_db(
    self,
    document_title,
    creation_timestamp,
    document_content_data
  ):
    
    title_id = ""
    document_id = str(uuid.uuid4())

    if not len(document_title) > 50:

      [conn, cursor] = self.db_connection()

      title_id_query = cursor.execute("""
        SELECT title_id FROM titles WHERE title = ?
      """, ( document_title, )
      )

      title_id_from_db = title_id_query.fetchone()

      if title_id_from_db == None:
        title_id = str(uuid.uuid4())

        cursor.execute("INSERT INTO titles VALUES (?, ?)",
          ( title_id, document_title, )
        )
      else:
        title_id = title_id_from_db[0]
      
      cursor.execute("INSERT INTO documents_metadata VALUES (?, ?, ?)",
        ( document_id, creation_timestamp, title_id, )
      )

      cursor.execute("INSERT INTO documents_data VALUES (?, ?)",
       ( document_id, document_content_data, )
      )

      conn.commit()
      conn.close()
    else:
      raise TitleTooLongError(f"Title: '{document_title}' Title is too long, max limit of 50 characters")
  
  def save_dummy_data_to_db(self):
    file_data = get_data_from_file("dummy_data.json")
    for document in file_data:
      document_title = document["title"]
      creation_timestamp = document["creation_timestamp"]
      document_content_data = document["content"]

      self.save_data_to_db(
        document_title,
        creation_timestamp,
        document_content_data
      )
