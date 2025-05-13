from unittest.mock import patch, MagicMock, mock_open
import os
import pandas as pd
import numpy as np

from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@patch("builtins.open", new_callable=mock_open)
@patch("os.path.exists")
@patch("os.listdir")
@patch("os.path.join", side_effect=lambda *args: "/".join(args))
@patch("subprocess.run")
@patch("pandas.read_csv")
@patch("src.handlers.model_handler.get_or_create_model")
@patch("src.handlers.model_handler.save_model")
@patch("src.handlers.scaler_handler.get_or_create_scaler")
@patch("src.handlers.scaler_handler.save_scaler")
@patch("utils.train_test_utils.train_model")
@patch("dotenv.load_dotenv")
@patch.dict(os.environ, {"WINDOW_SIZE": "5", "MODEL_NAME": "LSTM"})
def test_train_function(
    mock_dotenv, mock_train_model, mock_save_scaler, mock_get_scaler,
    mock_save_model, mock_get_model, mock_read_csv, mock_subprocess_run,
    mock_join, mock_listdir, mock_exists, mock_open_file
):
    from scripts.train_model import train

    mock_listdir.return_value = ["AAPL.csv.dvc"]
    mock_exists.side_effect = lambda path: not path.endswith(".dvc")

    df = pd.DataFrame({
        "date": pd.date_range(start="2020-01-01", periods=20),
        "cloture": np.random.rand(20)
    })
    mock_read_csv.return_value = df

    dummy_model = MagicMock()
    dummy_model.get_last_trained_date.return_value = pd.to_datetime("2020-01-10")
    mock_get_model.return_value = dummy_model

    dummy_scaler = MagicMock()
    mock_get_scaler.return_value = dummy_scaler
    mock_train_model.return_value = dummy_scaler

    # --- Call the function ---
    train()

    # --- Assertions ---
    mock_dotenv.assert_called()
    mock_read_csv.assert_called_once()
    mock_get_model.assert_called_once_with("AAPL", "LSTM")
    mock_train_model.assert_called_once()
    mock_save_model.assert_called_once()
    mock_save_scaler.assert_called_once()
