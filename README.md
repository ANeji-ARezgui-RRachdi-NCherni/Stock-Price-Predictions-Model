# Stock-Price-Predictions
A machine learning model capable of predicting stock prices as well as giving recommendations

---

## 📁 Repository Architecture

The repository is structured as follows:

```
```
Stock-Price-Predictions/
│── .github/
│   └── workflows/
│       └── ci.yml
│── data/
│   ├── processed/
│   └── raw/
│── notebooks/
│── src/
│   ├── prediction_model/
│   │   ├── data/
│   │   │   ├── __init__.py
│   │   │   └── data.py
│   │   ├── model/
│   │   │   ├── __init__.py
│   │   │   └── model.py
│   │   ├── __init__.py
│   │   └── main.py
│   ├── recommender_system/
│   │   ├── __init__.py
│   │   └── main.py
│   ├── web/
│   │   ├── back/
│   │   ├── front/
│   │   ├── __init__.py
│   │   └── main.py
│── tests/
│   ├── prediction_model/
│   │   ├── test_data.py
│   │   └── test_model.py
│   └── recommender_system/
│── utils/
│   └── constants.py
│── .gitignore
│── environment.yml
│── README.md
```
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
