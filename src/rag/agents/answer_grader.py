from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from typing import Literal
from dotenv import load_dotenv
import os


load_dotenv()
model_name = os.getenv('SIMPLE_TASK_MODEL')
api_key= os.getenv("GOOGLE_API_KEY_1")

class GradeAnswer(BaseModel):
    """Binary score to assess answer addresses question."""

    binary_score: Literal["yes", "no"] = Field(
        description="Answer addresses the question, 'yes' or 'no'"
    )


# LLM with function call
llm = ChatGoogleGenerativeAI(model=model_name, temperature=0, google_api_key=api_key)
structured_llm_grader = llm.with_structured_output(GradeAnswer)

# Prompt
system = """You are tasked with grading whether a given answer adequately addresses and resolves the associated question.

        Evaluate the answer carefully and determine if it satisfactorily resolves the question. Provide a binary assessment:
        - Output "yes" if the answer fully addresses and resolves the question.
        - Output "no" if the answer does not resolve the question or lacks sufficient relevance.

        # Steps
        1. Read and understand the question.
        2. Review the answer in the context of the question.
        3. Decide if the answer resolves the question completely and correctly.
        4. Output "yes" or "no" accordingly without additional explanation.

        # Output Format
        - A single word: either "yes" or "no", indicating whether the answer resolves the question."""

answer_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "User question: {question}, LLM answer: {answer}"),
    ]
)

answer_grader_agent = answer_prompt | structured_llm_grader