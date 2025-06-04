import os
import joblib
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model
from azure.ai.ml.constants import AssetTypes
from src.prediction_model.models import IModel
from src.factories.model_factory import create_model
from pathlib import Path
import pickle

FILE_PATH = Path(os.path.dirname(__file__))
MODEL_LOCAL_PATH = FILE_PATH / ".." / ".." / "pkl" / "models"

def _get_ml_client() -> MLClient:
    return MLClient(
        credential=DefaultAzureCredential(),
        subscription_id=os.environ["AZURE_SUBSCRIPTION_ID"],
        resource_group_name=os.environ["AZURE_RESOURCE_GROUP"],
        workspace_name=os.environ["AZURE_ML_WORKSPACE"]
    )

def get_or_create_model(stock: str, model_name: str, model_location: str) -> IModel:
    model = get_model(stock, model_location)
    if model is not None:
        return model
    return create_model(stock, model_name)

def get_model(stock: str, model_location: str) -> IModel | None:
    if model_location == "LOCAL":
        model_path = MODEL_LOCAL_PATH / f"{stock}.pkl"
        if not model_path.is_file():
            return None
        with open(model_path, "rb") as f:
            return pickle.load(f)

    elif model_location == "AZURE":
        ml_client = _get_ml_client()
        try:
            # NOTE: we’re explicitly asking for version=1 here. Change to latest_version=True if desired.
            model_asset = ml_client.models.get(name=f"{stock}-model", version=1)
            print(f"Found model asset: {model_asset.name} v{model_asset.version}")

            # Where Azure ML will dump the files
            download_dir = os.path.join("outputs", stock, "model")
            os.makedirs(download_dir, exist_ok=True)

            downloaded_path = ml_client.models.download(
                name=f"{stock}-model",
                version=model_asset.version,
                download_path=download_dir
            )
            print(f"Downloaded model to: {downloaded_path}")

            # Walk the subtree under download_dir
            pkl_files = []
            for dirpath, dirnames, filenames in os.walk(download_dir):
                for fn in filenames:
                    if fn.lower().endswith(".pkl"):
                        pkl_files.append(os.path.join(dirpath, fn))

            if not pkl_files:
                print(f"No .pkl files found under {download_dir} (or its subfolders)")
                return None

            # Prefer exactly "model.pkl" if it exists
            exact_model = [p for p in pkl_files if os.path.basename(p).lower() == "model.pkl"]
            if exact_model:
                model_path = exact_model[0]
            else:
                # Otherwise, just pick the first .pkl we found
                print(f"Warning: no file literally named 'model.pkl'; using {pkl_files[0]} instead.")
                model_path = pkl_files[0]

            print(f"Loading model from: {model_path}")
            return joblib.load(model_path)

        except Exception as e:
            print(f"Error loading model from Azure: {e}")
            print(f"Attempted to load model named: {stock}-model")
            return None

    else:
        raise NotImplementedError("MODEL_LOCATION must be 'LOCAL' or 'AZURE'.")


def save_model(model: IModel, model_location: str, stock: str):
    if model_location == "LOCAL":
        os.makedirs(MODEL_LOCAL_PATH, exist_ok=True)
        model_path = MODEL_LOCAL_PATH / f"{stock}.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

    elif model_location == "AZURE":
        outputs_dir = os.path.join("outputs", stock)
        os.makedirs(outputs_dir, exist_ok=True)

        # Save to outputs/{stock}/model.pkl
        model_file = os.path.join(outputs_dir, "model.pkl")
        joblib.dump(model, model_file)

        ml_client = _get_ml_client()
        model_asset = Model(
            path=outputs_dir,
            name=f"{stock}-model",
            type=AssetTypes.CUSTOM_MODEL,
            description=f"Model bundle for {stock}"
        )
        registered = ml_client.models.create_or_update(model_asset)
        print(f"Registered model '{registered.name}' (version {registered.version})")
    else:
        raise NotImplementedError("MODEL_LOCATION must be 'LOCAL' or 'AZURE'.")
