from src.prediction_model.models import IModel
from src.factories.model_factory import create_model
import os
from pathlib import Path
import pickle

FILE_PATH = Path(os.path.dirname(__file__))
MODEL_LOCAL_PATH = FILE_PATH / '..' / '..' / 'pkl' / 'models'

def get_or_create_model(stock: str, model_name: str, model_location: str) -> IModel:
    model = get_model(stock, model_location)
    if model != None:
        return model
    return create_model(stock, model_name)

def get_model(stock: str, model_location: str) -> IModel | None:
    if model_location == "LOCAL":
        model_path = MODEL_LOCAL_PATH / f'{stock}.pkl'
        if not model_path.is_file():
            return None
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    else:
        raise NotImplementedError("This method isn't implemented!")

def save_model(model: IModel, model_location: str, stock: str):
    if model_location == "LOCAL":
        model_path = MODEL_LOCAL_PATH / f'{stock}.pkl'
        if os.path.exists(MODEL_LOCAL_PATH) == False:
            os.makedirs(MODEL_LOCAL_PATH)
        with open(model_path, 'wb') as file:
            pickle.dump(model, file)
    else:
        raise NotImplementedError("This method isn't implemented!")