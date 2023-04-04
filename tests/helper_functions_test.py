from src.helper_functions import get_data_from_file

from unittest.mock import mock_open, patch

def test_get_data_from_file_returns_data():
  
  mock = mock_open(read_data='{"data": "data"}')

  with patch("builtins.open", mock) as mocked_open:
    assert get_data_from_file("fake_file") == {"data": "data"}
    mocked_open.assert_called_once_with("fake_file", "r")