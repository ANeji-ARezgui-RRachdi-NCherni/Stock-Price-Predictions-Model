from typing import Dict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# we need to change directory to import IModel interface
import sys,os
from pathlib import Path
sys.path.insert(0, str(Path(os.getcwd() / '..')))
from src.prediction_model.models.IModel import IModel


def split_dataset(dataset: pd.DataFrame, test_size: float = 0.2) -> tuple [pd.DataFrame, pd.DataFrame] :
    """
    Splits the dataset into training and testing sets.

    Args:
        dataset (pd.DataFrame): The dataset to split.
        test_size (float): The proportion of the dataset to include in the test split.

    Returns:
        tuple: A tuple containing the training and testing sets.
    """
    # Calculate the number of rows for the test set
    test_rows = int(len(dataset) * test_size)
    train_rows = len(dataset) - test_rows
    
    # Split the dataset
    train_set = dataset[:train_rows]
    test_set = dataset[train_rows:]

    return train_set, test_set

def get_target_from_dataset(dataset: pd.DataFrame) -> np.ndarray :
    """
    gets the target list from the dataset.

    Args:
        dataset (pd.DataFrame): The dataset from which we want to get the target feature.

    Returns:
        an array: An array containing the target.
    """
    Y = dataset["ouverture"]
    return np.array(Y)

def get_features_from_dataset(dataset: pd.DataFrame) -> np.ndarray :
    """
    gets the features from the dataset.

    Args:
        dataset (pd.DataFrame): The dataset from which we want to get the target feature (the first column "symbole" must be removed first).

    Returns:
        an array: An array containing the features.
    """   
    X = dataset.iloc[:,:]
    return np.array(X)

def train(models_dictionary: Dict[str, IModel], training_dataset: pd.DataFrame):
    x_train = get_features_from_dataset(training_dataset)
    y_train = get_target_from_dataset(training_dataset)
    for model in models_dictionary.values():
        model.train(x_train, y_train)

def evaluate(models_dictionary: Dict[str, IModel], test_dataset: pd.DataFrame, metric: str) -> Dict[str, float]:
    result = {}
    x_test = get_features_from_dataset(test_dataset)
    y_test = get_target_from_dataset(test_dataset)
    for model_name, model in models_dictionary.items():
        result[model_name] = model.evaluate(x_test, y_test, metric)
    return result

def plot_evaluation_result(eval_result: Dict[str, float], metric: str):
    plt.figure(figsize=(12, 6))
    plt.bar(eval_result.keys(), eval_result.values(), color=['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'brown', 'pink', 'gray', 'yellow'])
    plt.xlabel("Models")
    plt.ylabel(f"metric: {metric}")
    plt.title(f"Comparison of Models Based on {metric}")
    plt.xticks(rotation=45)
    plt.show()

