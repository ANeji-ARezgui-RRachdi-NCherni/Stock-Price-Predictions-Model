import os
import subprocess
import pandas as pd
from dotenv import load_dotenv
import logging

import sys
from pathlib import Path
sys.path.insert(0, str(Path(os.getcwd()) / '..'))
from src.handlers.model_handler import get_or_create_model, save_model
from src.handlers.scaler_handler import get_or_create_scaler, save_scaler
from utils.train_test_utils import train_model, evaluate
from enums import ValidationMetricEnum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def train():
    DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/processed")
    DATA_DIR = os.path.abspath(DATA_DIR)

    load_dotenv()

    WINDOW_SIZE = int(os.environ.get("WINDOW_SIZE")) 
    MODEL_NAME = os.environ.get("MODEL_NAME")
    MODEL_LOCATION = os.environ.get("MODEL_LOCATION")
    MODEL_EVAL_THRESHHOLD = float(os.environ.get("MODEL_EVAL_THRESHHOLD"))

    stocks_list = [f.replace(".csv.dvc", "") for f in os.listdir(DATA_DIR) if f.endswith(".csv.dvc")]
    all_models_evaluation = {}
    logger.info(f"found {len(stocks_list)} stocks")
    for stock in stocks_list:
        logger.info(f"training model: {MODEL_NAME} for stock: {stock}")
        dvc_file = os.path.join(DATA_DIR, f"{stock}.csv.dvc")
        csv_file = dvc_file.replace(".dvc", "")
        if not os.path.exists(csv_file):
            logger.info("pulling csv files")
            subprocess.run(["dvc", "pull", dvc_file], check=True, capture_output=True, text=True)
        if not os.path.exists(csv_file):
            logger.warning(f"{stock}.csv not found")
            continue
        df = pd.read_csv(csv_file, sep=";")
        model = get_or_create_model(stock, MODEL_NAME, MODEL_LOCATION)
        scaler = get_or_create_scaler(stock, MODEL_LOCATION)
        last_trained_date = model.get_last_trained_date()
        logger.info(f"model's old last trained date: {last_trained_date if last_trained_date else 'Never trained before'}")
        df["date"] = pd.to_datetime(df["date"])
        if last_trained_date:
            num_train_rows = len(df[df['date'] > last_trained_date])
        else:
            num_train_rows = len(df["date"]) - WINDOW_SIZE
        if num_train_rows == 0:
            logger.warning("No new rows to train ...")
            continue
        logger.info(f"Found {num_train_rows} rows to train the model with")
        new_last_trained_date = max(df["date"])
        logger.info(f"model's new last trained date: {new_last_trained_date}")
        full_model_name = f"{stock}"
        if last_trained_date:
            train_df = df.tail(WINDOW_SIZE + num_train_rows).copy()
            # if the model is already pre-trained on old data we evaluate the model predictions of the days post last trained date
            # based on the newly added data
            logger.info(f"evaluating {full_model_name} model on dates from {train_df[-num_train_rows]['date']} to {train_df[-1]['date']} using MAPE")
            train_df = train_df["cloture"].values.reshape(-1,1)
            model_evaluation = evaluate({full_model_name: (model, [], train_df)}, ValidationMetricEnum.MAPE, {full_model_name: scaler})
            if (model_evaluation[full_model_name] >= MODEL_EVAL_THRESHHOLD):
                logger.warning(
                    f"Model '{full_model_name}' (last trained on {last_trained_date}) exceeded the evaluation threshold for {ValidationMetricEnum.MAPE.name}: "
                    f"threshold={MODEL_EVAL_THRESHHOLD}, result={model_evaluation[full_model_name]}"
                )
            else:
                logger.info(
                    f"Model '{full_model_name}' (last trained on {last_trained_date}) passed evaluation for {ValidationMetricEnum.MAPE.name}: "
                    f"result={model_evaluation[full_model_name]}"
                )
            all_models_evaluation.update(model_evaluation)
        else:
            train_df = df.copy()
            train_df = train_df["cloture"].values.reshape(-1,1)
        scaler = train_model(model, full_model_name, train_df, scaler, WINDOW_SIZE, new_last_trained_date)
        logger.info(f"Training {stock} model done, saving model and scaler")
        save_model(model, MODEL_LOCATION, stock)
        save_scaler(scaler, MODEL_LOCATION, stock)
    
    # TODO: Maybe send the evaluation results for all models to some sort of a dashboard that shows a graph of the models perfomance after each run of the script, idk
    logger.info("Training script completed successfully")

if __name__ == "__main__":
    # Run the processing pipeline
    train()