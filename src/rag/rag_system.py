from typing import List, TypedDict
from langgraph.graph import StateGraph, END,  START
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import time
import os
from dotenv import load_dotenv
from .agents import *
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



def log_execution_time(func):
    """
    Decorator to log the execution time of a function.
    """
    def wrapper(*args, **kwargs):
        start_time = time.time()  # Record the start time
        result = func(*args, **kwargs)
        end_time = time.time()  # Record the end time
        execution_time = end_time - start_time
        print(f"Execution time for {func.__name__}: {execution_time:.4f} seconds")
        return result
    return wrapper

@log_execution_time
def check_topic_relevency(state:State):
    """
    Check if the question is relevant to the RAG system.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """
    question = state["question"]
    source = topic_checker.invoke({"question": question})
    if source.datasource == "off_topic":
        return "off_topic"
    elif source.datasource == "rag":
        return "rag"

@log_execution_time
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
    return {"topic": topic.topic, "question": question}

@log_execution_time
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

@log_execution_time
def retrieve(state:State):
    """
    Retrieve Documents

    Args:
        state (State): The state of the graph.

    Returns:
        state(dict): The state of the graph with the retrieved documents in a new key.    
    """
    embedded_question = state["embedded_question"]
    question = state["question"]
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
        k= 7,
        filter=filter
    )
    return {"documents": documents ,  "question": question }

@log_execution_time
def transform_query(state:State):
    """
    Rewrite the question for better understanding or relevance.
    """
    print("rewriting question")
    better_question = question_rewriter.invoke({"question": state["question"]})
    return {"question": better_question}

@log_execution_time
def off_topic(state:State):
    """
    Response for user questions that are off topic.

    Returns:
        state (dict): returns the state with a response indicating the question is off topic.
    """
    response = "I'm sorry, I only answer questions related to the Tunisian stock market and related news."
    return {"generation" : response}

@log_execution_time
def generate(state:State):
    """
    Generate a response based on the question and documents.

    Args:
        state (State): The state of the graph.

    Returns:
        state (dict): The state of the graph with the generated response in a new key.
    """
    question = state["question"]
    top_contexts = state["documents"]
    topic = state["topic"]
    match topic:
        case "news":
            agent = NewsAgent()
        case "stocks":
            agent = StockAgent()
        case "recommendation":
            agent = RecommenderAgent()
                
    generation_chain = agent.get_decision_chain()
    generation = generation_chain.invoke({"question": question, "context": top_contexts, "topic" : state["topic"]})
    return {"generation": generation, "question": question}


def create_agents_graph():

    workflow = StateGraph(State)

    workflow.add_node("classify_question",classify_question )
    workflow.add_node("off_topic", off_topic) 
    workflow.add_node("embed_question", embed_question)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate", generate)
    workflow.add_node("transform_query", transform_query)

    workflow.add_conditional_edges(
        START,
        check_topic_relevency,
            {
                "off_topic": "off_topic",
                "rag": "classify_question",
            }   
        )    
    workflow.add_edge("off_topic", END)
    workflow.add_edge("classify_question", "embed_question")
    workflow.add_edge("embed_question","retrieve")
    workflow.add_edge("retrieve","generate")
    workflow.add_edge("generate",END )

    app = workflow.compile()

    return app

