from src.prediction_model.models import IModel, ARIMAModel, LSTMModel, GRUModel
from dotenv import load_dotenv

load_dotenv()

def create_model(stock: str, model_name: str) -> IModel:
    if model_name is None:
        raise KeyError("The model name is not specified in the environment file!")
    match model_name:
        case "ARIMA":
            return ARIMAModel(stock)
        case "GRU":
            return GRUModel(stock)
        case "LSTM":
            return LSTMModel(stock)
        case _:
            return NotImplementedError("The given model name is not implemented yet, please choose another one!")