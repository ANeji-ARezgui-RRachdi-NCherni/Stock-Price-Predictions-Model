import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import pytest
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# we need to change directory to import modules
import sys,os
from pathlib import Path
sys.path.insert(0, str(Path(os.getcwd()) / '..' / '..'))
from src import IModel, ARIMAModel
from utils import split_dataset, get_features_target_from_dataset, plot_stock_graph, train, evaluate, plot_evaluation_result
from enums import ValidationMetricEnum

def test_split_dataset():
    data = pd.DataFrame({'a': range(10)})
    train_df, test_df = split_dataset(data, test_size=0.3)
    assert len(train_df) == 7
    assert len(test_df) == 3


def test_get_features_target_from_dataset_regular_case():
    arr = np.array([[i] for i in range(100)])
    X, Y = get_features_target_from_dataset(arr, False, closeColIdx=0, isArimaContext=False, window=10)
    assert X.shape[0] == 90
    assert X.shape[1:] == (10, 1)
    assert Y.shape[0] == 90

def test_get_features_target_from_dataset_arima_context():
    arr = np.array([[i] for i in range(10)])
    X, Y = get_features_target_from_dataset(arr, False, closeColIdx=0, isArimaContext=True)
    assert isinstance(X, np.ndarray)
    assert (X == Y).all()

def test_train_with_single_column():
    mock_model = Mock(spec=IModel)
    df = pd.DataFrame({'cloture': range(100)})
    models = {'mock': (mock_model, df, df)}
    scalers = train(models)
    assert 'mock' in scalers
    mock_model.train.assert_called()

def test_train_with_multi_column():
    mock_model = Mock(spec=IModel)
    df = pd.DataFrame({'date': pd.date_range("20210101", periods=100), 'cloture': range(100), 'volume': range(100)})
    models = {'mock': (mock_model, df, df)}
    scalers = train(models)
    assert 'mock' in scalers
    mock_model.train.assert_called()

def test_evaluate_success():
    mock_model = Mock(spec=IModel)
    mock_model.evaluate.return_value = 0.85
    df = pd.DataFrame({'cloture': range(100)})
    models = {'mock': (mock_model, df, df, df)}
    scalers = {'mock': MinMaxScaler().fit(df)}
    result = evaluate(models, ValidationMetricEnum.RMSE, scalers)
    assert result['mock'] == 0.85
    mock_model.evaluate.assert_called()

def test_evaluate_missing_scaler():
    mock_model = Mock(spec=IModel)
    df = pd.DataFrame({'cloture': range(100)})
    models = {'mock': (mock_model, df, df, df)}
    with pytest.raises(KeyError):
        evaluate(models, ValidationMetricEnum.RMSE, {})

def test_plot_evaluation_result_calls_plotting():
    eval_result = {"Model1": 0.9, "Model2": 0.8}
    with patch("matplotlib.pyplot.figure") as mock_figure, \
         patch("matplotlib.pyplot.bar") as mock_bar, \
         patch("matplotlib.pyplot.xlabel") as mock_xlabel, \
         patch("matplotlib.pyplot.ylabel") as mock_ylabel, \
         patch("matplotlib.pyplot.title") as mock_title, \
         patch("matplotlib.pyplot.xticks") as mock_xticks, \
         patch("matplotlib.pyplot.show") as mock_show:
        
        plot_evaluation_result(eval_result, "accuracy")
        
        mock_figure.assert_called_once()
        mock_bar.assert_called_once()
        mock_xlabel.assert_called_once()
        mock_ylabel.assert_called_once()
        mock_title.assert_called_once()
        mock_xticks.assert_called_once()
        mock_show.assert_called_once()


@patch("matplotlib.pyplot")
def test_plot_stock_graph_calls_plotting(mock_plt):
    dates = np.array([1, 2, 3])
    y_test = np.array([10, 20, 30])
    y_predict = np.array([12, 18, 33])
    with patch("matplotlib.pyplot.figure") as mock_figure, \
         patch("matplotlib.pyplot.plot") as mock_plot, \
         patch("matplotlib.pyplot.xlabel") as mock_xlabel, \
         patch("matplotlib.pyplot.ylabel") as mock_ylabel, \
         patch("matplotlib.pyplot.title") as mock_title, \
         patch("matplotlib.pyplot.legend") as mock_legend, \
         patch("matplotlib.pyplot.show") as mock_show:
        
        plot_stock_graph(dates, y_test, y_predict, "model")        

        mock_figure.assert_called_once()
        mock_plot.assert_called()
        mock_xlabel.assert_called_once()
        mock_ylabel.assert_called_once()
        mock_title.assert_called_once()
        mock_legend.assert_called_once()
        mock_show.assert_called_once()
    

if __name__ == "__main__":
    pytest.main()
