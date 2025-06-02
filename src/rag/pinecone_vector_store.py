from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec     

import os
from dotenv import load_dotenv
import time


load_dotenv()
pinecone_api_key = os.environ.get("PINECONE_API_KEY")
embedding_model = os.environ.get("EMBEDDING_MODEL")


def get_pinecone_vector_store(index_name):
    pc = Pinecone(api_key=pinecone_api_key)
    
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
    doc_embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model, task_type="RETRIEVAL_DOCUMENT")
    vectore_store = PineconeVectorStore(index=index, embedding=doc_embeddings)
    return vectore_store
