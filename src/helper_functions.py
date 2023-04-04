import json

def get_data_from_file(file):
  with open(file, "r") as f:
    data = json.load(f)

  return data