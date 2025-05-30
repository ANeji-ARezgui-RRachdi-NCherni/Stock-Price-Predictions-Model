import requests
from bs4 import BeautifulSoup, SoupStrainer
from datetime import datetime
import os
from dotenv import load_dotenv
import argparse

from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader

from pathlib import Path
import sys
sys.path.insert(0, str(Path(os.getcwd()) / '..'))
from src import get_pinecone_vector_store
from utils import PAGE_URL, NEWS_BASE_URL



load_dotenv()

embedding_model = os.getenv("EMBEDDING_MODEL")
index_name = os.getenv("INDEX_NAME")


def get_articles(date):
    """
    Scrape articles from the target page.
    
    Returns:
        articles: List of article objects with title, source, and date.
        
    """
    # Send request and parse
    response = requests.get(PAGE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Get today's date in DD/MM/YYYY format
    if not date:
        date = datetime.now().strftime('%d/%m/%Y')
        print(f"Using today's date: {date}")

    articles = []
    # Locate the specific table
    table = soup.find("table", class_="tablesorter tbl100_6 tbl3 mt37")

    if table:
        rows = table.find_all("tr")
        for row in rows:
            date_span = row.find("span", class_="sp1")
            link_tag = row.find("a", href=True)

            if date_span and link_tag:
                article_date = date_span.text.strip().split(" ")[0]
                if article_date == date:
                    article_url = link_tag["href"]
                    full_url = NEWS_BASE_URL + article_url
                    article={
                        "title": link_tag.text.strip(),
                        "link": full_url,
                        "date": article_date,
                        "source": "news"
                    }
                    articles.append(article)   
                    
    else:
        print("Articles Table not found on the page.")

    return articles


def process_urls(articles) -> list[Document]:
    """
    Load data from a list of URLs.
    
    Args:
        urls (Sequence): Sequence of URLs to load data from.
    
    Returns:
        docs: List of documents.
        
    """
    bs4_strainer = SoupStrainer(class_=("inarticle txtbig"))
    loader = WebBaseLoader(
        web_paths=[article["link"] for article in articles],
        bs_kwargs={"parse_only": bs4_strainer},
    )
    docs = loader.load()
    for i, doc in enumerate(docs):
        doc.page_content = doc.page_content.replace("\n", " ").replace("\r", " ").strip().strip("Tweet")
        # Extract the title and date from the corresponding article
        article = articles[i]
        doc.metadata = {
            "title": article["title"],
            "date": article["date"],
            "link": article["link"],
            "source": article["source"],
        }

    return docs

def store_docs(docs):
    """
    Store documents in Pinecone VectorStore.
    
    Args:
        docs (list[Document]): List of documents to store.
        
    """
    vector_store = get_pinecone_vector_store(index_name)
    
    try:
        vector_store.add_documents(docs)
        print(f"Stored {len(docs)} documents in Pinecone.")
    except Exception as e:
        print(f"Error storing documents in Pinecone: {e}")



def main(date):
    articles = get_articles(date)
    
    if len(articles) > 0: 
    # Process the articles and store them in Pinecone
        docs = process_urls(articles)
        store_docs(docs)

    else:
        print("No articles found for today.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and Storing automation for news articles.")
    parser.add_argument("--date", required=False, help="Articles date in dd/mm/YYYY format")
    args = parser.parse_args()
    main(args.date)    