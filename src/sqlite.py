import sqlite3

class SqliteDB:
  def __init__(self, database_name = "wiki_documents_db.db"):
    self.database_name = database_name

  def db_connection(self):
    try:
      conn = sqlite3.connect(self.database_name)
      cursor = conn.cursor()
    except sqlite3.Error as error:
      print(error)

    return conn, cursor
  
  def database_setup(self):

    sqlite_create_titles_table = """
      CREATE TABLE titles (
        title_id TEXT PRIMARY KEY NOT NULL,
        title TEXT UNIQUE NOT NULL
      )
    """

    sqlite_create_documents_metadata_table = """
      CREATE TABLE documents_metadata (
        document_id TEXT PRIMARY KEY NOT NULL,
        creation_timestamp TEXT NOT NULL,
        title_id TEXT NOT NULL
      )
    """

    sqlite_create_documents_data_table = """
      CREATE TABLE documents_data (
        document_id TEXT PRIMARY KEY NOT NULL,
        document_content TEXT NOT NULL
      )
    """

    [conn, cursor] = self.db_connection()

    try:
      cursor.execute(sqlite_create_titles_table)
      cursor.execute(sqlite_create_documents_metadata_table)
      cursor.execute(sqlite_create_documents_data_table)
      conn.commit()
    except sqlite3.Error as error:
      print(error)
      conn.rollback()
    
    conn.close()
  