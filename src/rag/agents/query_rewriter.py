from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os


load_dotenv()
model_name = os.getenv("SIMPLE_TASK_MODEL")

llm = ChatGoogleGenerativeAI(model=model_name, temperature=0)

system = """Re-write the input question to improve it for vectorstore retrieval. 
            Analyze the question carefully to understand its true semantic intent, then generate a clearer, more precise version optimized for searching vector databases. 
            Output only the re-written question with no extra text or explanation."""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        (
            "human",
            "Input question: {question}",
        ),
    ]
)

question_rewriter = prompt | llm | StrOutputParser()