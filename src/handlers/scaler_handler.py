import os
import joblib
from sklearn.preprocessing import MinMaxScaler
from azure.ai.ml import MLClient
from azure.identity import DefaultAzureCredential
from azure.ai.ml.entities import Model as ScalerModel
from azure.ai.ml.constants import AssetTypes
from pathlib import Path
import pickle

FILE_PATH = Path(os.path.dirname(__file__))
SCALER_LOCAL_PATH = FILE_PATH / ".." / ".." / "pkl" / "scalers"

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
        scaler_path = SCALER_LOCAL_PATH / f"{stock}.pkl"
        if not scaler_path.is_file():
            return None
        with open(scaler_path, "rb") as f:
            return pickle.load(f)

    elif model_location == "AZURE":
        ml_client = _get_ml_client()
        try:
            scaler_asset = ml_client.models.get(name=f"{stock}-scaler", version=1)
            print(f"Found scaler asset: {scaler_asset.name} v{scaler_asset.version}")

            download_dir = os.path.join("outputs", stock, "scaler")
            os.makedirs(download_dir, exist_ok=True)

            downloaded_path = ml_client.models.download(
                name=f"{stock}-scaler",
                version=scaler_asset.version,
                download_path=download_dir
            )
            print(f"Downloaded scaler to: {downloaded_path}")

            # Recursively gather all *.pkl files
            pkl_files = []
            for dirpath, dirnames, filenames in os.walk(download_dir):
                for fn in filenames:
                    if fn.lower().endswith(".pkl"):
                        pkl_files.append(os.path.join(dirpath, fn))

            if not pkl_files:
                print(f"No .pkl files found under {download_dir} (or its subfolders)")
                return None

            # Prefer exactly "scaler.pkl"
            exact_scaler = [p for p in pkl_files if os.path.basename(p).lower() == "scaler.pkl"]
            if exact_scaler:
                scaler_path = exact_scaler[0]
            else:
                print(f"Warning: no file literally named 'scaler.pkl'; using {pkl_files[0]} instead.")
                scaler_path = pkl_files[0]

            print(f"Loading scaler from: {scaler_path}")
            return joblib.load(scaler_path)

        except Exception as e:
            print(f"Error loading scaler from Azure: {e}")
            print(f"Attempted to load scaler named: {stock}-scaler")
            return None

    else:
        raise NotImplementedError("MODEL_LOCATION must be 'LOCAL' or 'AZURE'.")


def save_scaler(scaler: MinMaxScaler, model_location: str, stock: str):
    if model_location == "LOCAL":
        os.makedirs(SCALER_LOCAL_PATH, exist_ok=True)
        scaler_path = SCALER_LOCAL_PATH / f"{stock}.pkl"
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)

    elif model_location == "AZURE":
        outputs_dir = os.path.join("outputs", stock)
        os.makedirs(outputs_dir, exist_ok=True)

        # Save scaler under outputs/{stock}/scaler.pkl
        scaler_file = os.path.join(outputs_dir, "scaler.pkl")
        joblib.dump(scaler, scaler_file)

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
        raise NotImplementedError("MODEL_LOCATION must be 'LOCAL' or 'AZURE'.")
