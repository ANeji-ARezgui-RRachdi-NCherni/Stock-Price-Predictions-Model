from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import subprocess
import pandas as pd

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
    dvc_file = os.path.join(DATA_DIR, f"{company}.csv.dvc")
    if not os.path.exists(dvc_file):
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        csv_file = dvc_file.replace(".dvc", "")
        if not os.path.exists(csv_file):
            subprocess.run(["dvc", "pull", dvc_file], check=True)

        df = pd.read_csv(csv_file, sep=";")
        return {"columns": df.columns.tolist(), "data": df.to_dict(orient="records")}
    except subprocess.CalledProcessError:
        raise HTTPException(status_code=500, detail="Failed to pull data with DVC")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
