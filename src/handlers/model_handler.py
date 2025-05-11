from src.prediction_model.models import IModel
from src.factories.model_factory import create_model

def get_or_create_model(stock: str, model_name: str) -> IModel:
    # TODO: Check first if the model exists already in azure ML, if so bring it
    return create_model(stock, model_name)

def save_model(model: IModel):
    raise NotImplementedError("Method not implemented!")