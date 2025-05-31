from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os, sys
from pathlib import Path
import subprocess
import pandas as pd
sys.path.insert(0, str(Path(os.path.dirname(__file__)) / '..' / '..' / '..'))
from utils import predict
from src import get_model, get_scaler
from dotenv import load_dotenv
from dateutil.relativedelta import relativedelta

load_dotenv()

MODEL_LOCATION = os.environ.get("MODEL_LOCATION")

app = FastAPI()

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../../data/processed")
DATA_DIR = os.path.abspath(DATA_DIR)

# CORS config for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/companies")
def list_companies():
    try:
        return [f.replace(".csv.dvc", "") for f in os.listdir(DATA_DIR) if f.endswith(".csv.dvc")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stock/{company}")
def get_stock(company: str):
    WINDOW_SIZE = int(os.environ.get("WINDOW_SIZE")) 
    
    dvc_file = os.path.join(DATA_DIR, f"{company}.csv.dvc")
    if not os.path.exists(dvc_file):
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        csv_file = dvc_file.replace(".dvc", "")
        if not os.path.exists(csv_file):
            subprocess.run(["dvc", "pull", dvc_file], check=True, capture_output=True, text=True)
        df = pd.read_csv(csv_file, sep=";")
        model = get_model(company, MODEL_LOCATION)
        scaler = get_scaler(company, MODEL_LOCATION)

        if (model == None or scaler == None):
            raise HTTPException(status_code=403, detail="Model unavailable, Try later")
        df["date"] = pd.to_datetime(df["date"], format='%Y-%m-%d', dayfirst=True)
        most_recent_date = max(df["date"])
        if (model.get_last_trained_date() < most_recent_date or model.get_last_trained_date() > most_recent_date):
            raise HTTPException(status_code=403, detail="Model unavailable, Try later")
        cloture_col = df["cloture"].values.reshape(-1,1)
        predicted_data = predict(model, cloture_col, scaler, WINDOW_SIZE, WINDOW_SIZE)

        ## Add the predicted data
        new_date = most_recent_date
        for val in predicted_data:
            new_date = new_date + relativedelta(days = 1)
            df.loc[len(df)] = [new_date, val, val, val, val, 0] # date;ouverture;haut;bas;cloture;volume
            
        return {"columns": df.columns.tolist(), "data": df.to_dict(orient="records")}
    except subprocess.CalledProcessError as e:
        error_message = f"Failed to pull data with DVC. stdout: {e.stdout.strip() if e.stdout else ''}, stderr: {e.stderr.strip() if e.stderr else ''}"
        raise HTTPException(status_code=500, detail=error_message)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail=str(e))
