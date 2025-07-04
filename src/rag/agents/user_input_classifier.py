from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI 
from pydantic import BaseModel, Field

from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()
model_name = os.getenv('SIMPLE_TASK_MODEL')
api_key= os.getenv("GOOGLE_API_KEY_1")

# Data model
class ClassifyInput(BaseModel):
    """Classify user input into the most relevant topic."""

    topic: Literal["news", "stocks", "recommendation"] = Field(
        ...,
        description="Given a user input choose the topic of the question. The topics are: news, stocks, recommendation."
    )


# LLM with function call
llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, google_api_key= api_key)
structured_llm_router = llm.with_structured_output(ClassifyInput)

# Prompt
system = """

Classify the following user input into one of the following topics:
- stocks
- news
- recommendation
Respond only with the topic name.
"""
classify_user_input = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{user_input}"),
    ]
)

input_classifer = classify_user_input | structured_llm_router