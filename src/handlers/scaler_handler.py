import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model as ScalerModel
from azure.ai.ml.constants import AssetTypes


def _get_ml_client() -> MLClient:
    return MLClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
        workspace_name=os.environ["AZURE_ML_WORKSPACE"]
    )


def get_or_create_scaler(stock: str, scaler_name: str = "default_scaler"):
    """
    Try to fetch the latest registered scaler from Azure ML; if not found, return a new MinMaxScaler.
    """
    ml_client = _get_ml_client()
    try:
        scaler_asset = ml_client.models.get(name=scaler_name)
        download_dir = os.path.join("outputs", scaler_name)
        os.makedirs(download_dir, exist_ok=True)
        ml_client.models.download(name=scaler_name,
                                  version=scaler_asset.version,
                                  download_path=download_dir)
        scaler_path = os.path.join(download_dir, "scaler.pkl")
        return joblib.load(scaler_path)
    except Exception:
        return MinMaxScaler()


def save_scaler(scaler, scaler_name: str = "default_scaler"):
    """
    Save the scaler locally and register (or update) it in Azure ML as a model asset.
    """
    outputs_dir = os.path.join("outputs", scaler_name)
    os.makedirs(outputs_dir, exist_ok=True)
    scaler_path = os.path.join(outputs_dir, "scaler.pkl")
    joblib.dump(scaler, scaler_path)

    ml_client = _get_ml_client()
    scaler_asset = ScalerModel(
        path=outputs_dir,
        name=scaler_name,
        type=AssetTypes.CUSTOM_MODEL,
        description="MinMaxScaler bundle"
    )
    registered = ml_client.models.create_or_update(scaler_asset)
    print(f"Registered scaler '{registered.name}' (version {registered.version})")