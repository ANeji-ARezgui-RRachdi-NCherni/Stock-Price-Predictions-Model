from unittest.mock import patch, MagicMock
import pytest
from streamlit.testing.v1 import AppTest
@patch("src.web.front.app.requests.get")
def test_chart_renders_with_data(mock_get):
    from unittest.mock import MagicMock

    def side_effect(url, *args, **kwargs):
        mock_response = MagicMock()
        if url.endswith("/companies"):
            mock_response.status_code = 200
            mock_response.json.return_value = ["AB"]
        elif "/stock/AB" in url:
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "columns": ["date", "cloture"],
                "data": [
                    {"date": "2020-01-01", "cloture": 100},
                    {"date": "2020-01-02", "cloture": 102},
                ]
            }
        return mock_response

    mock_get.side_effect = side_effect

    at = AppTest.from_file("src/web/front/app.py")
    at.run(timeout=10)

    at.selectbox[0].select("AB")
    at.session_state["Select a company"] = "AB"
    at.run(timeout=10)

    # Assert no errors and a title exists — basic health check
    assert len(at.title) == 1
    assert len(at.error) == 0