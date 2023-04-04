import os.path
import json

from datetime import datetime
from flask import Flask, request, redirect

from src.sqlite import SqliteDB
from src.database_data_handlers import DatabaseManager
from src.document_store_actions import DocumentStoreActions

data_handler = DatabaseManager()
document_store_actions = DocumentStoreActions()

app = Flask(__name__)

@app.route("/")
def home():
    return "🚀 Welcome to My wikipedia! 🚀"

@app.route("/documents", methods=["GET"])
def get_all_available_titles():
  '''
  This endpoint returns a list of all available titles
  '''
  title_list = document_store_actions.get_titles()

  return title_list

@app.route("/documents/<title>", methods=["GET", "POST"])
def manage_document_revisions_for_a_title(title):
  '''
  GET: This endpoint returns a list of all available revisions for a document.
  POST: This endpoint allows a user to add new document revisions to titles
  '''
  if request.method == "GET":
    documents_list = document_store_actions.get_documents(title)

    return documents_list
  elif request.method == "POST":
    try:
      data = json.loads(request.data)
      content = data["content"]
      timestamp = datetime.now()
      document_store_actions.post_new_document_revision(title, timestamp, content)
    except Exception as error:
      print(error)
    finally:
      return {"message": f"New document saved to {title}"}
   
@app.route("/documents/<title>/<timestamp>", methods=["GET"])
def get_document_revision_at_a_given_timestamp(title, timestamp):
  '''
  This endpoint returns a document for a title
  as it was at a given timestamp.
  '''
  document_revision = document_store_actions.get_document_as_it_was_at_a_given_timestamp(title, timestamp)

  return document_revision

@app.route("/documents/<title>/latest", methods=["GET"])
def get_document_latest_revision(title):
  '''
  This endpoint returns the latest revision
  of a document for a given title.
  '''
  latest_document_revision = document_store_actions.get_latest_document_revision(title)

  return latest_document_revision

# Checking if a database file exists
is_database_created = os.path.isfile("wiki_documents_db.db")

if __name__ == "__main__":
  if not is_database_created:
    sqlite_db = SqliteDB()
    sqlite_db.database_setup()
    data_handler.save_dummy_data_to_db()
  else:
     print("Database has already been created")

  app.run(
    host="127.0.0.1",
    port=8080,
    debug=True
  )