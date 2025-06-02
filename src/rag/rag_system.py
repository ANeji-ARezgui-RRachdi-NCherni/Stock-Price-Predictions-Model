from typing import List, TypedDict
from langgraph.graph import StateGraph, END,  START
from langchain_core.documents import Document
import time
import os
from dotenv import load_dotenv

from .agents import *
from .pinecone_vector_store import get_pinecone_vector_store



load_dotenv()
index_name = os.getenv("INDEX_NAME")


n_agent = NewsAgent()
s_agent = StockAgent()
r_agent = RecommenderAgent()
vector_store = get_pinecone_vector_store(index_name)


class State(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        topic: topic of the question('news', 'stocks', 'recommendation')
        documents: list of documents
    """
    question: str
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
    source = topic_checker.invoke({"question": state["question"]})
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
    return {"topic": topic.topic}


@log_execution_time
def retrieve(state:State):
    """
    Retrieve Documents

    Args:
        state (State): The state of the graph.

    Returns:
        state(dict): The state of the graph with the retrieved documents in a new key.    
    """
    topic = state["topic"]
    filter = {'source' : topic} if topic != "recommendation" else None
    retriever =vector_store.as_retriever(
    search_type="similarity",
    search_kwargs={
        "k": 7, 
        "filter": filter  
    },
)
    documents = retriever.invoke(input=state["question"])
    return {"documents": documents }

@log_execution_time
def transform_query(state:State):
    """
    Rewrite the question for better understanding or relevance.
    """
    better_question = question_rewriter.invoke({"question": state["question"]})
    return {"question": better_question}

@log_execution_time
def off_topic(state:State):
    """
    Response for user questions that are off topic.
    Args:
        state (State): The state of the graph.
    Returns:
        state (dict): adds  a response to the state indicating the question is off topic.
    """
    response = off_topic_responder.invoke({"question": state["question"]})
    return {"generation": response}

@log_execution_time
def generate_news(state:State):
    """
    Generate a response based on the question and documents.

    Args:
        state (State): The state of the graph.

    Returns:
        state (dict): The state of the graph with the generated response in a new key.
    """
    agent = n_agent     
    generation_chain = agent.get_decision_chain()
    generation = generation_chain.invoke({"question": state["question"], "context": state["documents"]})
    return {"generation": generation}

@log_execution_time
def generate_stocks(state:State):
    """
    Generate a response based on the question and documents.

    Args:
        state (State): The state of the graph.

    Returns:
        state (dict): The state of the graph with the generated response in a new key.
    """
    agent = s_agent     
    generation_chain = agent.get_decision_chain()
    generation = generation_chain.invoke({"question": state["question"], "context": state["documents"]})
    return {"generation": generation}
@log_execution_time
def generate_recommendation(state:State):
    """
    Generate a response based on the question and documents.

    Args:
        state (State): The state of the graph.

    Returns:
        state (dict): The state of the graph with the generated response in a new key.
    """
    agent = r_agent     
    generation_chain = agent.get_decision_chain()
    generation = generation_chain.invoke({"question": state["question"], "context": state["documents"]})
    return {"generation": generation}

@log_execution_time
def grade_answer(state:State):
    """
    Grade the generated answer.

    Args:
        state (State): The state of the graph.

    Returns:
        state (dict): The state of the graph with the graded answer in a new key.
    """
    grade = answer_grader_agent.invoke({"question": state["question"], "answer": state["generation"]})
    return grade.binary_score

@log_execution_time
def route_query(state:State):
    """
    passes the topic of the question to the next node, to decide which agent to use.
    """
    return state["topic"]


def create_agents_graph():

    workflow = StateGraph(State)

    workflow.add_node("off_topic", off_topic) 
    workflow.add_node("classify_question", classify_question)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("generate_news", generate_news)
    workflow.add_node("generate_stocks", generate_stocks)
    workflow.add_node("generate_recommendation", generate_recommendation)
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
    workflow.add_edge("classify_question","retrieve")
    workflow.add_conditional_edges(
        "retrieve",
        route_query,
        {
            "news": "generate_news",
            "stocks": "generate_stocks",
            "recommendation": "generate_recommendation"
        })
    workflow.add_conditional_edges(
        "generate_news",
        grade_answer,
        {
            "yes":END,
            "no": "transform_query"
        }
    )
    workflow.add_conditional_edges(
        "generate_stocks",
        grade_answer,
        {
            "yes":END,
            "no": "transform_query"
        }
    )
    workflow.add_conditional_edges(
        "generate_recommendation",
        grade_answer,
        {
            "yes":END,
            "no": "transform_query"
        }
    )
    workflow.add_edge("transform_query", "retrieve")

    app = workflow.compile()
    
    return app



