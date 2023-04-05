class Error(Exception):
    pass

class TitleTooLongError(Error):
  def __init__(self, message):
    self.message = message
  def __str__(self):
    return repr(self.message)

class NoDataInDatabase(Error):
  def __init__(self, message):
    self.message = message
  def __str__(self):
    return repr(self.message)

class TitleNotFound(Error):
  def __init__(self, message):
    self.message = message
  def __str__(self):
    return repr(self.message)

class NoDocumentCreatedAtTimestamp(Error):
  def __init__(self, message):
    self.message = message
  def __str__(self):
    return repr(self.message)
  
class NoChangesDetected(Error):
  def __init__(self, message):
    self.message = message
  def __str__(self):
    return repr(self.message)
