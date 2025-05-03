from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import dotenv
import os

dotenv.load_dotenv()
model_name = os.environ.get("LLM_MODEL")


prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an assistant for question-answering tasks.
            You're a skilled communicator with a knack for turning complex information into clear and concise responses.\n
            Synthesize the retrieved information into a concise and coherent response based on the user question.\n
            Keep the response short and to the point, avoiding unnecessary details.\n
            If you are not able to retrieve the information then respond with "I\'m sorry, I couldn\'t find the information 
            you\'re looking for.""",),
            (
            "human",
            """ 
            Question: {question} 
            Context: {context}  
            """
        ),
]
)

generative_llm= ChatGoogleGenerativeAI(model=model_name, temperature=0)

generation_chain= prompt | generative_llm | StrOutputParser()