import sys
sys.path.append(".")
from unittest.mock import patch, MagicMock
from app.api_client import get_districts


def test_get_districts_calls_correct_endpoint():
    with patch("app.api_client.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = [{"district_id": 1, "district_name": "Test"}]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        get_districts.clear()  # bypass st.cache_data for the test
        result = get_districts()

        mock_get.assert_called_once_with("http://localhost:8000/districts")
        assert result[0]["district_name"] == "Test"