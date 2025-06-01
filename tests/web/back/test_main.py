import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from src.web.back.main import app
from sklearn.preprocessing import MinMaxScaler
import os, sys
from pathlib import Path
sys.path.insert(0, str(Path(os.path.dirname(__file__)) / '..' / '..' / '..'))
import pandas as pd
from src import LSTMModel


@patch("src.web.back.main.os.listdir")
@patch("dotenv.load_dotenv")
@patch.dict(os.environ, {"WINDOW_SIZE": "1", "MODEL_NAME": "LSTM", "MODEL_LOCATION": "LOCAL", "DISABLE_BACKEND_CACHE": True})
def test_get_companies(mock_dotenv, mock_listdir):
    mock_listdir.return_value = ["AB.csv.dvc", "AL.csv.dvc"]
    
    with TestClient(app) as client:
        response = client.get("/companies")
    
    assert response.status_code == 200
    assert response.json() == ["AB", "AL"]

@patch("src.web.back.main.get_model")
@patch("src.web.back.main.get_scaler")
@patch("src.web.back.main.predict")
@patch("src.web.back.main.os.path.exists")
@patch("src.web.back.main.pd.read_csv")
@patch("src.web.back.main.subprocess.run")
@patch("dotenv.load_dotenv")
@patch.dict(os.environ, {"WINDOW_SIZE": "1", "MODEL_NAME": "LSTM", "MODEL_LOCATION": "LOCAL", "DISABLE_BACKEND_CACHE": True})
def test_get_stock_valid(mock_dotenv, mock_subprocess, mock_read_csv, mock_exists, mock_predict, mock_get_scaler, mock_get_model):
    # Access mocks to avoid unused argument warnings
    _ = mock_dotenv
    _ = mock_subprocess
    mock_exists.return_value = True
    mock_df = pd.DataFrame({"date": ["2020-01-01"], "ouverture": [100], "haut": [100], "bas": [100], "cloture": [100], "volume": [0]})
    mock_read_csv.return_value = mock_df
    mock_predict.return_value = [100]
    mock_get_scaler.return_value = MinMaxScaler()
    model = LSTMModel("AB")
    model.last_trained_date = max(pd.to_datetime(mock_df["date"], format='%Y-%m-%d', dayfirst=True))
    mock_get_model.return_value = model
    
    with TestClient(app) as client:
        response = client.get("/stock/AB")
    
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert "data" in data
    assert data["columns"] == ["date", "ouverture", "haut", "bas", "cloture", "volume"]
    assert data["data"][0]["cloture"] == 100

@patch("src.web.back.main.os.path.exists")
@patch("dotenv.load_dotenv")
@patch.dict(os.environ, {"WINDOW_SIZE": "1", "MODEL_NAME": "LSTM", "MODEL_LOCATION": "LOCAL", "DISABLE_BACKEND_CACHE": True})
def test_get_stock_not_found(mock_dotenv, mock_exists):
    mock_exists.return_value = False
    
    with TestClient(app) as client:
        response = client.get("/stock/UNKNOWN")
    
    assert response.status_code == 404