from pinecone import Pinecone, ServerlessSpec     
import os
from dotenv import load_dotenv
import time


load_dotenv()
pinecone_api_key = os.environ.get("PINECONE_API_KEY")

def get_pinecone_index(index_name: str) -> Pinecone.Index:
    """
    Initialize and return a Pinecone index.

    Args:
        pinecone_api_key (str): Pinecone API key.

    Returns:
        pinecone.Index: Initialized Pinecone index.
    """
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
    return index