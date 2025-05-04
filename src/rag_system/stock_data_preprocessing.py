from langchain_text_splitters import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path
import sys
sys.path.insert(0, str(Path(os.getcwd()) / '..'))
from utils import get_pinecone_vector_store

load_dotenv()
index_name = os.getenv("INDEX_NAME")




data_path = os.environ.get('DATA_PATH')

def process_stock_data(stock_data_dir):
    """
    Load data from a CSV file.
    
    Args:
        file_path (str): Path to the CSV file.
    
    Returns:
        stock_data: List of Documents.
    """
    stock_data = []
    for file in os.listdir(stock_data_dir):
        file_path = os.path.join(stock_data_dir, file)
        df= pd.read_csv(file_path)
        df['text']= df.apply(lambda row: f"Stock {row['stock']} on date {row['date']}, opening price {row['ouverture']:.2f}, closing price {row['cloture']:.2f}, volume {row['volume']:,.2f}.", axis=1)
        stock_data += df['text'].tolist()

    stock_data = "\n".join(stock_data)
    text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"],
            chunk_size=1024,  # chunk size (characters)
            chunk_overlap=0,  # chunk overlap (characters)
            # add_start_index=True,  # track index in original document
        )
    splits = text_splitter.split_text(stock_data)
 
    return splits

def preprocess_stock_data(data_path):
    for filename in os.listdir(data_path):
        stock_name=filename.split('_')[0]
        file_path = os.path.join(data_path, filename)
        df = pd.read_csv(file_path)
        df['stock'] = stock_name
        df= df[4000:]
        df.to_csv(file_path, index=False)

def store_stock_data(stock_data_dir):
    """
    Store stock data in Pinecone VectorStore.
    
    Args:
        stock_data_dir (str): Directory containing stock data CSV files.
        
    """
    vector_store = get_pinecone_vector_store(index_name)
    stock_data = process_stock_data(stock_data_dir)
    try:
        ids = vector_store.add_documents(stock_data)
    except Exception as e:
        print(f"Error adding documents: {e}")  
        ids = []

    return ids