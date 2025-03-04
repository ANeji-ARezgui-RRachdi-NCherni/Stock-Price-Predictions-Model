# Stock-Price-Predictions
A machine learning model capable of predicting stock prices as well as giving recommendations

---

## 📁 Repository Architecture

The repository is structured as follows:

```
stock-price-predictions/
│── .github/
│   └── workflows/
│       └── ci.yml  # CI/CD pipeline configuration
│── data/
│   ├── processed/  # Processed datasets
│   └── raw/        # Raw datasets
│── notebooks/      # Jupyter notebooks for exploration and analysis
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
│   ├── web/
│   │   ├── back/  # Backend implementation (to be defined)
│   │   ├── front/ # Frontend implementation (to be defined)
│   │   ├── __init__.py
│   │   └── main.py  # Web application entry point
│── tests/
│   ├── prediction_model/
│   │   ├── test_data.py  # Unit tests for data processing
│   │   └── test_model.py # Unit tests for model
│   └── recommender_system/
│── utils/
│   └── constants.py  # Utility constants
│── .gitignore       # Git ignore file
│── environment.yml  # Dependencies and environment configuration
│── README.md        # Project documentation
```

---

## 🛠️ Setup Instructions

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

### **3. Set Up Data Directories**
Create the following directories (if not already created):
```bash
mkdir data/raw
mkdir data/processed
mkdir notebooks
```

### **4. Run the Project**
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
 - Data Loading: Load raw data from CSV files.
 - Feature Engineering: Transform raw data into useful features.
 - Model Training: Train machine learning models with various algorithms.
 - Evaluation: Assess model performance with relevant metrics.
 - Visualization: Generate plots for data and results analysis.

---

Feel free to contribute or open issues to enhance the repository. Let me know if you face any issues during setup!
