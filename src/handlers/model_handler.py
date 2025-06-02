import os
import joblib
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes
from src.prediction_model.models import IModel
from src.factories.model_factory import create_model
import os
from pathlib import Path
import pickle

FILE_PATH = Path(os.path.dirname(__file__))
MODEL_LOCAL_PATH = FILE_PATH / '..' / '..' / 'pkl' / 'models'

def _get_ml_client() -> MLClient:
    return MLClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
        workspace_name=os.environ["AZURE_ML_WORKSPACE"]
    )

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
    elif model_location == "AZURE":
        ml_client = _get_ml_client()
        try:
            # Get latest version of the registered model
            model_asset = ml_client.models.get(name=stock)
            # Download to local outputs folder
            download_dir = os.path.join("outputs", stock)
            os.makedirs(download_dir, exist_ok=True)
            ml_client.models.download(name=stock,
                                    version=model_asset.version,
                                    download_path=download_dir)
            model_path = os.path.join(download_dir, "model.pkl")
            return joblib.load(model_path)
        except Exception:
            # Not registered yet: return None
            return None
    else:
        raise NotImplementedError("This method isn't implemented!")

def save_model(model: IModel, model_location: str, stock: str):
    if model_location == "LOCAL":
        model_path = MODEL_LOCAL_PATH / f'{stock}.pkl'
        if os.path.exists(MODEL_LOCAL_PATH) == False:
            os.makedirs(MODEL_LOCAL_PATH)
        with open(model_path, 'wb') as file:
            pickle.dump(model, file)
    elif model_location == "AZURE":
        outputs_dir = os.path.join("outputs", stock)
        os.makedirs(outputs_dir, exist_ok=True)
        model_path = os.path.join(outputs_dir, "model.pkl")
        joblib.dump(model, model_path)

        ml_client = _get_ml_client()
        model_asset = Model(
            path=outputs_dir,
            name=stock,
            type=AssetTypes.CUSTOM_MODEL,
            description=f"Model bundle for {stock}"
        )
        registered = ml_client.models.create_or_update(model_asset)
        print(f"Registered model '{registered.name}' (version {registered.version})")
    else:
        raise NotImplementedError("This method isn't implemented!")
