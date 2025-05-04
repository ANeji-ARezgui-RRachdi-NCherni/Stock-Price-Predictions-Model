import os
from unittest.mock import patch, MagicMock
from streamlit.testing.v1 import AppTest

@patch.dict(os.environ, {"BACKEND_URL": "http://localhost:8000"})
@patch.dict(os.environ, {"FRONTEND_CACHE_EXPIRATION_TIME": "28800"})
@patch("requests_cache.CachedSession.get")

## TODO: We should Add other tests after implemeting the other widgets (1 test per widget at least)
def test_data_and_predict_widget(mock_get):

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

    at.button._list[1].click()
    at.run(timeout=10)

    at.selectbox[0].select("AB")
    at.session_state["Select a company"] = "AB"
    at.run(timeout=10)

    # Assert no errors — basic health check
    assert len(at.error) == 0