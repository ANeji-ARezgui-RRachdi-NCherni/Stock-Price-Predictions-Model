import os
import joblib
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes
from src.factories.model_factory import create_model

def _get_ml_client() -> MLClient:
    return MLClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
        workspace_name=os.environ["AZURE_ML_WORKSPACE"]
    )


def get_or_create_model(stock: str, model_name: str):
    """
    Try to fetch the latest registered model from Azure ML; if not found, create a new local model.
    """
    ml_client = _get_ml_client()
    try:
        # Get latest version of the registered model
        model_asset = ml_client.models.get(name=model_name)
        # Download to local outputs folder
        download_dir = os.path.join("outputs", model_name)
        os.makedirs(download_dir, exist_ok=True)
        ml_client.models.download(name=model_name,
                                  version=model_asset.version,
                                  download_path=download_dir)
        model_path = os.path.join(download_dir, "model.pkl")
        return joblib.load(model_path)
    except Exception:
        # Not registered yet: create new model instance
        return create_model(stock, model_name)


def save_model(model, model_name: str):
    """
    Save the model locally and register (or update) it in Azure ML.
    """
    outputs_dir = os.path.join("outputs", model_name)
    os.makedirs(outputs_dir, exist_ok=True)
    model_path = os.path.join(outputs_dir, "model.pkl")
    joblib.dump(model, model_path)

    ml_client = _get_ml_client()
    model_asset = Model(
        path=outputs_dir,
        name=model_name,
        type=AssetTypes.CUSTOM_MODEL,
        description=f"Model bundle for {model_name}"
    )
    registered = ml_client.models.create_or_update(model_asset)
    print(f"Registered model '{registered.name}' (version {registered.version})")