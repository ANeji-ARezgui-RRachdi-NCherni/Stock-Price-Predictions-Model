from typing import Dict
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler 
from enums import ValidationMetricEnum
from datetime import datetime

# we need to change directory to import IModel interface
import sys,os
from pathlib import Path
sys.path.insert(0, str(Path(os.getcwd()) / '..'))
from src import IModel, ARIMAModel


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

def get_features_target_from_dataset(dataset: np.ndarray, ShouldOnlyKeepCloseCol: bool, closeColIdx: int , isArimaContext: bool, window:int = 60, )-> tuple[np.ndarray, np.ndarray] :
    X = []
    Y = []
    if isArimaContext == True:
        return dataset.flatten(), dataset.flatten()
    for i in range(window, dataset.shape[0]):
        X.append(dataset[i-window:i])
        y_to_append = dataset[i]
        if (ShouldOnlyKeepCloseCol):
            y_to_append = y_to_append[closeColIdx] ## index of the cloture column
        Y.append(y_to_append)
    return np.array(X), np.array(Y)

def train_model(model: IModel, model_name: str, dataset: pd.DataFrame | np.ndarray, old_scaler: MinMaxScaler, window_size: int, last_trained_date: datetime) -> MinMaxScaler:
    model_dict = {model_name: (model, dataset, pd.DataFrame([]))} # we don't care about the test dataset
    if old_scaler:
        scaler_dict = {model_name: old_scaler}
    else:
        scaler_dict = None
    scaler = train(model_dict, window_size, scaler_dict=scaler_dict, last_trained_date=last_trained_date)[model_name]
    return scaler

def train(models_dictionary: Dict[str, tuple[IModel, pd.DataFrame | np.ndarray, pd.DataFrame | np.ndarray]], window_size: int = 60, scaler_dict: Dict[str, MinMaxScaler] = None, last_trained_date: datetime = datetime.today()) -> Dict[str, MinMaxScaler]:
    new_scaler_dict = {}
    for name, tuple in models_dictionary.items():
        print(f"training {name} model ...")
        if scaler_dict == None or (name not in scaler_dict) or scaler_dict.get(name) == None:
            scaler = MinMaxScaler()
        else :
            scaler = scaler_dict.get(name)
        model = tuple[0]
        df = tuple[1]
        ShouldOnlyKeepCloseCol = df.shape[1] > 1 # if the dataframe has more than one column we need to keep cloture only as target
        isArimaContext = isinstance(model, ARIMAModel)
        if ShouldOnlyKeepCloseCol :
            df_copy = df.copy()
            cols_to_drop = df_copy.columns[df_copy.columns.str.match('date')]
            df_copy.drop(cols_to_drop, axis=1, inplace=True)
            df_transformed = scaler.fit_transform(df_copy)
            closeColIdx = df_copy.columns.get_loc('cloture')
        else :
            df_transformed = scaler.fit_transform(df)
            closeColIdx = 0
        x_train, y_train = get_features_target_from_dataset(df_transformed, ShouldOnlyKeepCloseCol, closeColIdx=closeColIdx, isArimaContext=isArimaContext, window=window_size)
        model.train(x_train, y_train, last_trained_date)
        new_scaler_dict[name] = scaler
    return new_scaler_dict

def predict(model: IModel, dataset: np.ndarray, scaler: MinMaxScaler, num_days: int, window_size: int) -> np.ndarray:
    last_n_days = scaler.transform(dataset[-window_size: ]).flatten()
    output = np.array([])
    for i in range(num_days):
        print(f'output: {output}, length: {output.__len__()}')
        print(f'last {window_size} days: {last_n_days}, length: {last_n_days.__len__()}')
        predicted_value = model.predict(last_n_days.reshape(1,-1))
        transformed_predicted_value = scaler.inverse_transform(predicted_value)
        last_n_days = np.delete(last_n_days, 0)
        last_n_days = np.append(last_n_days, predicted_value)
        output = np.append(output, transformed_predicted_value)
    return output

def evaluate(models_dictionary: Dict[str, tuple[IModel, pd.DataFrame, pd.DataFrame, pd.DataFrame]], metric: ValidationMetricEnum, scaler_dict: Dict[str, MinMaxScaler]) -> Dict[str, float]:
    result = {}
    for model_name, tuple in models_dictionary.items():
        print(f"evaluating {model_name} model ...")
        model = tuple[0]
        test_df = tuple[2]
        scaler = scaler_dict.get(model_name) 
        if scaler == None:
            raise KeyError(f"Scaler couldn't be found for model: {model_name}")
        ShouldOnlyKeepCloseCol = test_df.shape[1] > 1
        isArimaContext = isinstance(model, ARIMAModel)
        if ShouldOnlyKeepCloseCol :
            test_df_copy = test_df.copy()
            cols_to_drop = test_df_copy.columns[test_df_copy.columns.str.match('date')]
            test_df_copy.drop(cols_to_drop, axis=1, inplace=True)
            test_dataset_transformed = scaler.transform(test_df_copy)
            closeColIdx = test_df_copy.columns.get_loc('cloture')
        else :
            test_dataset_transformed = scaler.transform(test_df)
            closeColIdx = 0   
        scale = 1/scaler.scale_[closeColIdx]         
        x_test, y_test = get_features_target_from_dataset(test_dataset_transformed, ShouldOnlyKeepCloseCol, closeColIdx=closeColIdx, isArimaContext=isArimaContext)
        result[model_name] = model.evaluate(x_test, y_test, metric, scale)
    return result

def plot_evaluation_result(eval_result: Dict[str, float], metric: str):
    plt.figure(figsize=(12, 6))
    plt.bar(eval_result.keys(), eval_result.values(), color=['red', 'blue', 'green', 'purple', 'orange', 'cyan', 'brown', 'pink', 'gray', 'yellow'])
    plt.xlabel("Models")
    plt.ylabel(f"metric: {metric}")
    plt.title(f"Comparison of Models Based on {metric}")
    plt.xticks(rotation=45)
    plt.show()

def plot_stock_graph(dates: np.ndarray, y_test: np.ndarray, y_predict: np.ndarray, model_name: str):
    plt.figure(figsize=(12, 6))
    plt.plot(dates, y_test, label='Actual Prices')
    plt.plot(dates, y_predict, label='Predicted Prices')
    plt.title(f'{model_name} Model Predictions vs Actual')
    plt.xlabel('Time')
    plt.ylabel('Price')
    plt.legend()
    plt.show()
