import os
from dotenv import load_dotenv
import pandas as pd 
import bs4

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_pinecone import PineconeVectorStore
# from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from chonkie import SemanticChunker
from markitdown import MarkItDown
import time
import getpass
from pinecone import Pinecone, ServerlessSpec 


load_dotenv()

if not os.getenv("PINECONE_API_KEY"):
    os.environ["PINECONE_API_KEY"] = getpass.getpass("Enter your Pinecone API key: ")

pinecone_api_key = os.environ.get("PINECONE_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")

pc = Pinecone(api_key=pinecone_api_key)



data_path = os.environ.get('DATA_PATH')
# db_location=os.environ.get('CHROMA_DB')
# db_exists = os.path.exists(db_location)



index_name = "langchain-test-index"  # change if desired

existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
index_exists = index_name in existing_indexes
if not index_exists:
    pc.create_index(
        name=index_name,
        dimension=768,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    while not pc.describe_index(index_name).status["ready"]:
        time.sleep(1)

index = pc.Index(index_name)


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
    

def process_urls(urls) -> list[Document]:
    """
    Load data from a list of URLs.
    
    Args:
        urls (Sequence): Sequence of URLs to load data from.
    
    Returns:
        splits: List of documents.
        
    """
    bs4_strainer = bs4.SoupStrainer(class_=("h1n mob30", "inarticle txtbig"))
    loader = WebBaseLoader(
        web_paths=urls,
        bs_kwargs={"parse_only": bs4_strainer},
    )
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # chunk size (characters)
            chunk_overlap=200,  # chunk overlap (characters)
            add_start_index=True,  # track index in original document
        )
    splits = text_splitter.split_documents(docs)

    return splits


urls = ("https://www.ilboursa.com/marches/le-directeur-general-de-banque-zitouna-nabil-el-madani-limoge_52322",
        "https://www.ilboursa.com/marches/la-turquie-s-engage-dans-l-exploration-petroliere-et-gaziere-en-libye_52271",
        "https://www.ilboursa.com/marches/kilani-holding-ne-prevoit-pas-de-retirer-la-sta-de-la-cote-de-la-bourse_52315")

query_embeddings = GoogleGenerativeAIEmbeddings(model =embedding_model, task_type="RETRIEVAL_QUERY") 
doc_embeddings = GoogleGenerativeAIEmbeddings(model =embedding_model, task_type="RETRIEVAL_DOCUMENT") 
vector_store = PineconeVectorStore(index=index, embedding=doc_embeddings)

if not index_exists:    
    splits = process_stock_data(data_path)
    vector_store.add_texts(splits)
    vector_store.add_documents(process_urls(urls))



    


    