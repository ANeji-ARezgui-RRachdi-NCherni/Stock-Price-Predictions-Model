from sklearn.preprocessing import MinMaxScaler
import os
from pathlib import Path
import pickle

FILE_PATH = Path(os.path.dirname(__file__))
SCALER_LOCAL_PATH = FILE_PATH / '..' / '..' / 'pkl' / 'scalers'

def get_or_create_scaler(stock: str, model_location: str) -> MinMaxScaler:
    scaler = get_scaler(stock, model_location)
    if scaler == None:
        return MinMaxScaler()

def get_scaler(stock: str, model_location: str) -> MinMaxScaler | None:
    if model_location == "LOCAL":
        scaler_path = SCALER_LOCAL_PATH / f'{stock}.pkl'
        if scaler_path.is_file() == False:
            return None
        with open(scaler_path, 'rb') as file:
            scaler = pickle.load(file)
        return scaler
    else:
        raise NotImplementedError("This method isn't implemented!")

def save_scaler(scaler: MinMaxScaler, model_location: str, stock: str):
    if model_location == "LOCAL":
        scaler_path = SCALER_LOCAL_PATH / f'{stock}.pkl'
        if os.path.exists(SCALER_LOCAL_PATH) == False:
            os.makedirs(SCALER_LOCAL_PATH)
        with open(scaler_path, 'wb') as file:
            pickle.dump(scaler, file)
    else:
        raise NotImplementedError("This method isn't implemented!")