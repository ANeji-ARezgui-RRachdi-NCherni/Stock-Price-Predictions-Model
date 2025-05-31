import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.web.back.main import app

@patch("src.web.back.main.os.listdir")
def test_get_companies(mock_listdir):
    mock_listdir.return_value = ["AB.csv.dvc", "AL.csv.dvc"]
    
    with TestClient(app) as client:
        response = client.get("/companies")
    
    assert response.status_code == 200
    assert response.json() == ["AB", "AL"]

@patch("src.web.back.main.os.path.exists")
@patch("src.web.back.main.pd.read_csv")
@patch("src.web.back.main.subprocess.run")
def test_get_stock_valid(mock_subprocess, mock_read_csv, mock_exists):
    mock_exists.return_value = True
    mock_df = MagicMock()
    mock_df.columns.tolist.return_value = ["date", "cloture"]
    mock_df.to_dict.return_value = [{"date": "2020-01-01", "cloture": 100}]
    mock_read_csv.return_value = mock_df
    
    with TestClient(app) as client:
        response = client.get("/stock/AB")
    
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "data" in data
    assert data["columns"] == ["date", "cloture"]
    assert data["data"][0]["cloture"] == 100

@patch("src.web.back.main.os.path.exists")
def test_get_stock_not_found(mock_exists):
    mock_exists.return_value = False
    
    with TestClient(app) as client:
        response = client.get("/stock/UNKNOWN")
    
    assert response.status_code == 404