from typing import List, TypedDict
from langgraph.graph import StateGraph, END,  START
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_google_genai import GoogleGenerativeAIEmbeddings

import os
from dotenv import load_dotenv
from .graph_nodes import *
from .pinecone_vector_store import get_pinecone_vector_store



load_dotenv()
embedding_model = os.getenv("EMBEDDING_MODEL")
index_name = os.getenv("INDEX_NAME")

class State(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        documents: list of documents
    """
    question: str
    embedded_question: List[float] = []
    documents: List[Document]= []
    topic: str = ""
    generation :str =""



def classify_question(state:State):
    """
    Classify the question into a topic.

    Args:
        state (State): The state of the graph.

    Returns:
        state (dict): The state of the graph with the classified topic in a new key.
    """
    question = state["question"]
    topic = input_classifer.invoke({"user_input": question})
    return {"topic": topic, "question": question}

def embed_question(state:State):
    """
    Embed the question using the embedding model.

    Args:
        state (State): The state of the graph.

    Returns:
        state (dict): The state of the graph with the embedded question in a new key.
    """
    question = state["question"]
    query_embeddings = GoogleGenerativeAIEmbeddings(model =embedding_model, task_type="RETRIEVAL_QUERY") 
    q_embed = query_embeddings.embed_query(text=question)
    return {"embedded_question": q_embed, "question": question}

def retrieve(state:State):
    """
    Retrieve Documents

    Args:
        state (State): The state of the graph.

    Returns:
        state(dict): The state of the graph with the retrieved documents in a new key.    
    """
    embedded_question= state["embedded_question"]
    question= state["question"]
    topic = state["topic"]
    vector_store = get_pinecone_vector_store(index_name)
    if topic == "news":
        filter = {"source": "news"}
    elif topic == "stocks":
        filter = {"source": "stock_data"}
    else:
        filter = None      

    documents = vector_store.similarity_search_by_vector_with_score(
        embedding=embedded_question,
        k= 20,
        filter=filter
        )
    documents = [d[0] for d in documents if d[1] > 0.4]  # Filter out low similarity scores
    print(f"Retrieved {len(documents)} documents")
    return {"documents": documents ,  "question": question }

def transform_query(state:State):

        print("rewriting question")
        better_question = question_rewriter.invoke({"question": state["question"]})
        return ({"question": better_question})

def off_topic(state:State):
    """
    Resonse for user questions that are off topic.

    Returns:
        state (dict): returns the state with a response indicating the question is off topic.
    """
    response = "I'm sorry, I only answer questions related to the Tunisian stock market and related news."
    return {"generation" : response}


def route_question(state:State):
    """
    Route question to RAG or off topic if it is not relevent.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "off_topic":
        return "off_topic"
    elif source.datasource == "vectorstore":
        return "vectorstore"

def generate(state:State):
        """
        Generate a response based on the question and documents.

        Args:
            state (State): The state of the graph.

        Returns:
            state (dict): The state of the graph with the generated response in a new key.
        """
        question = state["question"]
        documents = state["documents"]
        top_contexts = [(doc.page_content, doc.metadata['link'], doc.metadata['source']) for doc in documents]
        generation = generation_chain.invoke({"question": question, "context": top_contexts, "topic" : state["topic"]})
        return {"generation": generation, "question": question , "documents": documents }


def create_workflow():

    workflow = StateGraph(State)

    workflow.add_node("classify_question",classify_question )
    workflow.add_node("off_topic", off_topic) 
    workflow.add_node("embed_question", embed_question)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_node("transform_query", transform_query)

    workflow.add_conditional_edges(
        START,
        route_question,
            {
                "off_topic": "off_topic",
                "vectorstore": "classify_question",
            }   
        )    
    workflow.add_edge("classify_question", "embed_question")
    workflow.add_edge("off_topic", END)
    workflow.add_edge("embed_question","retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate",END )

    app = workflow.compile()

    return app
