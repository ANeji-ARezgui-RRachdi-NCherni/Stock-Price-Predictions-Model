from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from typing import List
import subprocess
from dotenv import load_dotenv
import os
import pandas as pd
from pathlib import Path
from datetime import date
from dateutil.relativedelta import relativedelta

import sys
sys.path.insert(0, str(Path(os.getcwd()) / '..'))
from utils import STOCK_DATA_URL
from src import get_pinecone_vector_store



load_dotenv()
index_name = os.environ.get("INDEX_NAME")

DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/processed")
DATA_PATH = os.path.abspath(DATA_PATH)


def delete_old_stock_data():
    """
    Delete old stock data files from Pinecone vectorstore.
    """
    vector_store = get_pinecone_vector_store(index_name)
    ids = vector_store.index.list(prefix="stock#")
    try:
        vector_store.delete(ids=list(ids))
        # Delete old stock data files from the local directory  
        print("Old stock data deleted successfully.")
    except Exception as e:
        print(f"Error deleting old stock data: {e}")

def fetch_stock_data():
    """
    Fetch stock data from cloud storage.
        
    Returns:
        df_list: List of dataframes containing stock data.
    """
    df_list = []
    for dvc_file in os.listdir(DATA_PATH):
        if dvc_file.endswith(".dvc"):
            try:
                csv_file = os.path.join(DATA_PATH, dvc_file.replace(".dvc", ""))
                if not os.path.exists(csv_file):
                    subprocess.run(["dvc", "pull", os.path.join(DATA_PATH, dvc_file)], check=True, capture_output=True, text=True)
                df = pd.read_csv(csv_file, sep=";")
                stock_name=dvc_file.split('.')[0]
                df['stock'] = stock_name
                df_list.append(df)
            except subprocess.CalledProcessError as e:
                error_message = f"Failed to pull data with DVC. stdout: {e.stdout.strip() if e.stdout else ''}, stderr: {e.stderr.strip() if e.stderr else ''}"
                raise Exception(error_message)
            except Exception as e:
                raise Exception( str(e))    
    return df_list

def preprocess_stock_data(df_list:List [pd.DataFrame]) -> List[pd.DataFrame]:
    """
    Preprocess stock data by filtering for recent dates.
    
    Args:
        df_list (List[pd.DataFrame]): list of dataframes containing stock data to process.

    Returns:
        filtered_dfs: List of filtered dataframes.        
    """
    two_years_ago = date.today() - relativedelta(years=2)
    formatted_date = two_years_ago.strftime("%Y-%m-%d")
    filtered_dfs = []
    for df in df_list:
        filtered_df = df[df['date'] >= formatted_date]
        if filtered_df.empty:
            print(f"No data available for {df['stock'][0]} after {formatted_date}. Skipping this stock.")
            continue
        filtered_dfs.append(filtered_df)

    return filtered_dfs
def process_stock_data(df_list:List [pd.DataFrame]) -> List[str]:
    """
    Transform stock data for knowledge base storage .
    
    Args:
        df_list (List[pd.DataFrame]): list of dataframes  to process.
    
    Returns:
        stock_data: List of Documents.
    """
    text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n"],
            chunk_size=32768,  #power of 2
            chunk_overlap=0,      
        )
    documents = []
    ids =[]
    for df in df_list:
        stock_data = []
        stock = df['stock'].iloc[0]
        df = df.copy()    
        df['text']= df.apply(lambda row: f"Stock {row['stock']} on date {row['date']}, opening price {row['ouverture']:.2f}, closing price {row['cloture']:.2f}, volume {row['volume']:,.2f}.", axis=1)
        stock_data += df['text'].tolist()
        stock_data = "\n".join(stock_data)
        if len(stock_data) > 40000: # pinecone limit is 40KB metadata size per document 
            stock_data = text_splitter.split_text(stock_data)
            document1 = Document(page_content=stock_data[0], metadata={"title":stock ,"date":df['date'].iloc[-1], "link": STOCK_DATA_URL,"source": "stock_data"})
            document2 = Document(page_content=stock_data[1], metadata={"title":stock ,"date":df['date'].iloc[-1], "link": STOCK_DATA_URL,"source": "stock_data"})
            id1 = "stock#"+stock+"#1"
            id2 = "stock#"+stock+"#2"
            documents.extend([document1, document2])
            ids.extend([id1, id2])
        else:
            document = Document(page_content=stock_data, metadata={"title":stock ,"date":df['date'].iloc[-1], "link": STOCK_DATA_URL,"source": "stock data"})
            id = "stock#"+stock+"#1"
            documents.append(document)
            ids.append(id)
        
    return documents, ids



def store_stock_data(docs,ids, batch_size=559):
    """
    Store stock data in Pinecone VectorStore.
    
    Args:
        stock_data_dir (str): Directory containing stock data CSV files.
        
    """
    vector_store = get_pinecone_vector_store(index_name)
    n_docs = len(docs)
    for i in range(0, n_docs, batch_size):
        if i + batch_size > i + n_docs: 
            batch = docs[i:i + n_docs]
            ids = ids[i:i + n_docs]
        else:
            batch = docs[i:i + batch_size]
            ids = ids[i:i + batch_size]
        try:
            vector_store.add_documents(batch, ids=ids)
        except Exception as e:
            print(f"Error adding documents: {e}")  



def main():
    delete_old_stock_data()
    df_list = fetch_stock_data()
    filtered_dfs = preprocess_stock_data(df_list)
    docs,ids = process_stock_data(filtered_dfs)
    store_stock_data(docs,ids)
    

if __name__ == "__main__":
    main()    