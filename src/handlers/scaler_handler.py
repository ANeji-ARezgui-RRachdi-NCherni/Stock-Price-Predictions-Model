import os
import joblib
from sklearn.preprocessing import MinMaxScaler
import os
from pathlib import Path
import pickle
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model as ScalerModel
from azure.ai.ml.constants import AssetTypes


FILE_PATH = Path(os.path.dirname(__file__))
SCALER_LOCAL_PATH = FILE_PATH / '..' / '..' / 'pkl' / 'scalers'

def _get_ml_client() -> MLClient:
    return MLClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
        workspace_name=os.environ["AZURE_ML_WORKSPACE"]
    )

def get_or_create_scaler(stock: str, model_location: str) -> MinMaxScaler:
    scaler = get_scaler(stock, model_location)
    if scaler is None:
        return MinMaxScaler()
    return scaler

def get_scaler(stock: str, model_location: str) -> MinMaxScaler | None:
    if model_location == "LOCAL":
        scaler_path = SCALER_LOCAL_PATH / f'{stock}.pkl'
        if scaler_path.is_file() == False:
            return None
        with open(scaler_path, 'rb') as file:
            scaler = pickle.load(file)
        return scaler
    elif model_location == "AZURE":
        ml_client = _get_ml_client()
        try:
            scaler_asset = ml_client.models.get(name=f"{stock}-scaler" , latest_version=True)
            download_dir = os.path.join("outputs", stock)
            os.makedirs(download_dir, exist_ok=True)
            ml_client.models.download(name=f"{stock}-scaler",
                                    version=scaler_asset.version,
                                    download_path=download_dir)
            scaler_path = os.path.join(download_dir, "scaler.pkl")
            return joblib.load(scaler_path)
        except Exception:
            return None
    else:
        raise NotImplementedError("This method isn't implemented!")

def save_scaler(scaler: MinMaxScaler, model_location: str, stock: str):
    if model_location == "LOCAL":
        scaler_path = SCALER_LOCAL_PATH / f'{stock}.pkl'
        if os.path.exists(SCALER_LOCAL_PATH) == False:
            os.makedirs(SCALER_LOCAL_PATH)
        with open(scaler_path, 'wb') as file:
            pickle.dump(scaler, file)
    elif model_location == "AZURE":
        outputs_dir = os.path.join("outputs", stock)
        os.makedirs(outputs_dir, exist_ok=True)
        scaler_path = os.path.join(outputs_dir, "scaler.pkl")
        joblib.dump(scaler, scaler_path)
        joblib.dump(scaler, scaler_path)
        ml_client = _get_ml_client()
        scaler_asset = ScalerModel(
            path=outputs_dir,
            name=f"{stock}-scaler",
            type=AssetTypes.CUSTOM_MODEL,
            description="MinMaxScaler bundle"
        )
        registered = ml_client.models.create_or_update(scaler_asset)
        print(f"Registered scaler '{registered.name}' (version {registered.version})")
    else:
        raise NotImplementedError("This method isn't implemented!")
