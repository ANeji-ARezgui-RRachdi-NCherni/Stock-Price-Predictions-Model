from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI 
from pydantic import BaseModel, Field

from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()
model_name = os.getenv('SIMPLE_TASK_MODEL')

# Data model
class TopicCheck(BaseModel):
    """Check if the user Question is relevent to the RAG or not"""

    datasource: Literal["rag", "off_topic"] = Field(
        ...,
        description="Given a user question choose to route it to rag or not if it is not relevent.",
    )


# LLM with function call
llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)
structured_llm_router = llm.with_structured_output(TopicCheck)

# Prompt
system = """
You are an expert at routing a user question to RAG or decide if it is not relevent.
The RAG's vectorstore contains documents related to stock data in Tunisia for different Tunisian stocks.
The vectorstore also contains information about latetst news related to the Tunisian economy and stock market.
Use the vectorstore for questions on these topics.
"""
route_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)

topic_checker = route_prompt | structured_llm_router