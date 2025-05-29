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
    generation :str =""



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

def retrieve(state):
    """
    Retrieve Documents

    Args:
        state (State): The state of the graph.

    Returns:
        state(dict): The state of the graph with the retrieved documents in a new key.    
    """
    embedded_question= state["embedded_question"]
    question= state["question"]
    vector_store = get_pinecone_vector_store(index_name)
    documents = vector_store.similarity_search_by_vector_with_score(
        embedding=embedded_question,
        k=5,
        )
    documents = [d[0] for d in documents]
    print(f"Retrieved {len(documents)} documents")
    return {"documents": documents ,  "question": question }

def grade_documents(state: State):

        print("---CHECK DOCUMENT RELEVNECE TO QUESTION ---")
        question = state['question']
        documents = state['documents']

        filtered_docs=[]
        for d in documents:

            score = retrieval_grader.invoke(
                {"question": question, "document": d}
            )
            print(score)
            grade= score.binary_score
            if grade == "yes":
                print(f"Document is relevant to the question")
                filtered_docs.append(d)
            else:
                print(f"Document is not relevant to the question") 
                continue
        return {"documents": filtered_docs, "question": question }

def transform_query(state:State):

        print("rewriting question")
        better_question = question_rewriter.invoke({"question": state["question"]})
        return ({"question": better_question})

def web_search(state):
    """
    Web search based on the re-phrased question.

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): Updates documents key with appended web results
    """

    print("---WEB SEARCH---")
    question = state["question"]

    # Web search
    web_search_tool = TavilySearchResults(k=3)
    docs = web_search_tool.invoke({"query": question})
    web_results = "\n".join([d["content"] for d in docs])
    web_results = [Document(page_content=web_results, metadata = {"link": d["url"], "source":"web"}) for d in docs]

    return {"documents": web_results, "question": question}


def route_question(state):
    """
    Route question to web search or RAG.

    Args:
        state (dict): The current graph state

    Returns:
        str: Next node to call
    """

    print("---ROUTE QUESTION---")
    question = state["question"]
    source = question_router.invoke({"question": question})
    if source.datasource == "web_search":
        print("---ROUTE QUESTION TO WEB SEARCH---")
        return "web_search"
    elif source.datasource == "vectorstore":
        print("---ROUTE QUESTION TO RAG---")
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
        generation = generation_chain.invoke({"question": question, "context": top_contexts})
        return {"generation": generation, "question": question , "documents": documents }

def grade_generation_v_documents_and_question(state):
    """
    Determines whether the generation is grounded in the document and answers question.

    Args:
        state (dict): The current graph state

    Returns:
        str: Decision for next node to call
    """

    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader_agent.invoke(
        {"documents": documents, "generation": generation}
    )
    grade = score.binary_score

    # Check hallucination
    if grade == "yes":
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        # Check question-answering
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader_agent.invoke({"question": question, "generation": generation})
        grade = score.binary_score
        if grade == "yes":
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"

def create_workflow():

    workflow = StateGraph(State)
    workflow.add_conditional_edges(
        START,
        route_question,
            {
                "web_search": "web_search",
                "vectorstore": "embed_question",
            }   
        )

    workflow.add_node("embed_question", embed_question)
    workflow.add_node("retrieve", retrieve)
    workflow.add_node("web_search", web_search) 
    workflow.add_node("grade_documents", grade_documents)
    workflow.add_node("transform_query", transform_query)
    workflow.add_node("generate", generate)

    
    workflow.add_edge("web_search", "generate")
    workflow.add_edge("embed_question","retrieve")
    workflow.add_edge("retrieve", "grade_documents")
    workflow.add_conditional_edges(
        "grade_documents",
        lambda state: ("generate" if len(state["documents"]) > 0 else "transform_query"),
        {
            "transform_query": "transform_query",
            "generate": "generate",
        }   
    )
    workflow.add_conditional_edges(
        "transform_query",
        route_question,
            {
                "web_search": "web_search",
                "vectorstore": "retrieve",
            }   
        )
    workflow.add_conditional_edges(
        "generate",
        grade_generation_v_documents_and_question,
        {
             "useful": END,
             "not useful": "generate",   
             "not supported": "transform_query",
             
        }
    )

    app = workflow.compile()

    return app
