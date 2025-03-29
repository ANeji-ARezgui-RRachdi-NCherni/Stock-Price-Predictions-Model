import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import pytest
import matplotlib.pyplot as plt

# we need to change directory to import modules
import sys
sys.path.append('../')
from src.prediction_model.models.IModel import IModel
from utils.train_test_utils import split_dataset, get_target_from_dataset, get_features_from_dataset, train, evaluate, plot_evaluation_result
sys.path.append('/tests')

def test_split_dataset():
    data = pd.DataFrame({"col1": range(10)})
    train_set, test_set = split_dataset(data, test_size=0.2)
    assert len(train_set) == 8
    assert len(test_set) == 2
    
    # Edge cases
    train_set, test_set = split_dataset(data, test_size=0.0)
    assert len(train_set) == 10
    assert len(test_set) == 0

def test_get_target_from_dataset():
    data = pd.DataFrame({"symbole": ['A', 'B', 'C'], "ouverture": [10, 20, 30]})
    target = get_target_from_dataset(data)
    assert isinstance(target, np.ndarray)
    assert target.tolist() == [10, 20, 30]

def test_get_features_from_dataset():
    data = pd.DataFrame({"symbole": ['A', 'B', 'C'], "feature1": [1, 2, 3]})
    features = get_features_from_dataset(data)
    assert isinstance(features, np.ndarray)
    assert features.shape == (3, 2)  # Vérifie que la colonne symbole est bien incluse
    assert features.tolist() == [['A',1],['B',2],['C',3]]

def test_train():
    mock_model = Mock(spec=IModel)
    models_dict = {"mock_model": mock_model}
    data = pd.DataFrame({"symbole": ['A', 'B'], "ouverture": [10, 20]})
    train(models_dict, data)
    mock_model.train.assert_called()

def test_evaluate():
    mock_model = Mock(spec=IModel)
    mock_model.evaluate.return_value = 0.95
    models_dict = {"mock_model": mock_model}
    data = pd.DataFrame({"symbole": ['A', 'B'], "ouverture": [10, 20]})
    result = evaluate(models_dict, data, "accuracy")
    assert result == {"mock_model": 0.95}
    mock_model.evaluate.assert_called()

def test_plot_evaluation_result():
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

if __name__ == "__main__":
    pytest.main()
