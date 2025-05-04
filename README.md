# Stock-Price-Predictions
A machine learning project capable of predicting stock prices and providing recommendations, built with modern MLOps practices. This project leverages DVC for dataset versioning with Azure Blob Storage and uses Azure ML for automated model training and deployment.
---

## 📁 Repository Architecture

The repository is structured as follows:

```
stock-price-predictions/
│── .github/
│   └── workflows/  # Pipelines
│── .dvc            # Dvc config folder
│── enums           # Enums folder
│── data/
│   ├── processed/  # Processed datasets
│   └── raw/        # Raw datasets
│── notebooks/      # Jupyter notebooks for exploration and analysis
│── scripts/        # Scripts for the jobs/pipelines
│── src/
│   ├── prediction_model/
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── data.py  # Data preprocessing
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   └── model.py  # ML model implementation
│   │   ├── __init__.py
│   │   └── main.py  # Main script for model execution
│   ├── recommender_system/
│   │   ├── __init__.py
│   │   └── main.py  # Recommender system implementation
│   └── web/
│       ├── back/  # Backend implementation (to be defined)
│       ├── front/ # Frontend implementation (to be defined)
│       ├── __init__.py
│       └── main.py  # Web application entry point
│── tests/
│   ├── prediction_model/
│   ├── scripts/
│   ├── utils/
│   └──  web/
│── utils/ # Utility module
│   └── constants.py  # Utility constants
│── .dvcignore       # Dvc ignore file
│── .env.example     # Example of the .env file
│── .gitignore       # Git ignore file
│── environment.yml  # Dependencies and environment configuration
└── README.md        # Project documentation
```

---
##  MLOps Workflow Overview

Our project workflow is organized into three main pipelines:

### **1. Data Ingestion & Versioning**
- A daily (or manual) script fetches raw data and stores it locally in data/raw/.
- DVC tracks the raw datasets, and dvc push uploads the actual files to Azure Blob Storage (in the datasets container).

### **2. Data Processing Pipeline**
- A processing script cleans and transforms the raw data, saving the results in data/processed/.
- Again, DVC tracks these processed files, and dvc push stores them in Azure Blob Storage.

### **3. Model Training & Deployment Pipeline**
- A GitHub Actions workflow (triggered when processed data updates) uses dvc pull to fetch the latest processed data.
- An Azure ML job is submitted to train the model using the fetched data.
- Once training is complete, the model is registered and can later be deployed as a REST API endpoint using Azure ML.

##  Setup Instructions

Follow these steps to set up the project on your local machine:

### **1. Clone the Repository**
First, clone this repository to your local machine:
```bash
git clone https://github.com/anasneji2002/Stock-Price-Predictions.git
cd Stock-Price-Predictions
```

### **2. Create a Virtual Environment and install Dependencies**
```bash
conda env create -f environment.yml

conda activate Stock_Price_Prediction
# in case it didn't work run conda ini then close and re-open the terminal 
```
### **3. Authenticate with Azure**  
Before working with DVC or Azure ML, log in to Azure:
```bash
az login
```
Ensure your session is active:
```bash
az account show
```

### **4. Set Up Data Directories**
Make sure the following directories exist (they're tracked locally as empty folders for DVC):
```bash
mkdir data/raw
mkdir data/processed
```
### **5. Fetching & Versioning Raw Data**
#### **1. Fetch Data**
Use your data-fetching script to download raw data to data/raw/:
```bash
python scripts/fetch_data.py
```
#### **2. Track with DVC**
```bash
dvc add data/raw/stock_prices.csv
git add data/raw/stock_prices.csv.dvc
git commit -m "Add raw stock prices dataset"
```
#### **3. Push to Azure Blob Storage**
```bash
dvc push
```
### **6. Processing Data**
#### **1. Process Data**
Run your processing script to transform raw data and save the output in data/processed/:
```bash
python scripts/preprocess_data.py
```
#### **2. Track Processed Data**
```bash
dvc add data/processed/clean_stock_prices.csv
git add data/processed/clean_stock_prices.csv.dvc
git commit -m "Add processed stock prices dataset"
```
#### **3. Push Processed Data to Azure Blob Storage**
```bash
dvc push
```

### **7. Run the Project**
Run the main script to start the project:
```bash
python src/main.py
```

---

## 🧪 Testing
Run the unit tests to ensure everything works correctly:
```bash
pytest
```

---

## ✨ Features
 - Data Ingestion: Load and version raw data using DVC with Azure Blob Storage.
 - Feature Engineering: Transform raw data into clean, feature-rich datasets.
 - Model Training: Train machine learning models with various algorithms on processed data using Azure ML.
 - Evaluation: Assess model performance with relevant metrics.
 - Visualization: Generate plots for data and results analysis.
 - Web Application: A full-stack app that uses the latest deployed model to serve predictions and recommendations.
---

Feel free to contribute or open issues to enhance the repository. Let me know if you face any issues during setup!
