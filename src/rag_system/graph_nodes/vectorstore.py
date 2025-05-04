import os
from dotenv import load_dotenv
import pandas as pd 

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from pathlib import Path
import sys
sys.path.insert(0, str(Path(os.getcwd()) / '..'/ '..'))
from utils import get_pinecone_index


load_dotenv()
embedding_model = os.getenv("EMBEDDING_MODEL")



data_path = os.environ.get('DATA_PATH')

index_name = "langchain-test-index"  # change if desired
print("getting index")
index = get_pinecone_index(index_name)


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


# def process_pdf(file_path):
#     """
#     Load data from a PDF file.
    
#     Args:
#         file_path (str): Path to the PDF file.
    
#     Returns:
#         list: Loaded data as a list of IDs.
#     """
#     md = MarkItDown()
#     result = md.convert(file_path)
#     chunker = SemanticChunker(
#             embedding_model=doc_embeddings,
#             threshold=0.5,
#             chunk_size=512,
#             min_sentences=1
#         )
#     chunks = chunker.chunk(result.text_content)
#     all_splits = [Document(page_content=chunk.text) for chunk in chunks]
#     try:
#         ids = vector_store.add_documents(all_splits)
#     except Exception as e:
#         print(f"Error adding documents: {e}")  
#         ids = []
#     return ids      
    

query_embeddings = GoogleGenerativeAIEmbeddings(model =embedding_model, task_type="RETRIEVAL_QUERY") 
doc_embeddings = GoogleGenerativeAIEmbeddings(model =embedding_model, task_type="RETRIEVAL_DOCUMENT") 
vector_store = PineconeVectorStore(index=index, embedding=doc_embeddings)
print("Vector Store Initialized")

# if not index_exists:    
#     splits = process_stock_data(data_path)
#     vector_store.add_texts(splits)




    


    