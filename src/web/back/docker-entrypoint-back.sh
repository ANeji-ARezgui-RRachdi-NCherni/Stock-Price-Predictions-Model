set -e

source /opt/conda/etc/profile.d/conda.sh
conda activate stock-backend

# Move to the repository root (so that .dvc/config & data/processed exist)
cd /app
dvc remote list

#  Pull the “data/processed” folder from your Azure Blob remote
#  This ensures the actual CSVs appear under /app/data/processed/
dvc pull --force

cd /app/src/web/back
uvicorn main:app --host 0.0.0.0 --port 8000
