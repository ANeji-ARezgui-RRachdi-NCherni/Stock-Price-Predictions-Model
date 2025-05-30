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
            """You are a financial assistant that provides accurate and relevant answers based only on the retrieved documents.

            Use the provided `context` to generate a clear and informative response that matches the specified `topic`. 
            Do not make up information or speculate beyond the documents.

            If the context does not include sufficient information to answer the user's question, respond with:
            > "I'm sorry, I couldn't find enough information to answer that question based on the current data."""),
            
            (
            "human",
            """ 
                Task:
                Write a complete and helpful response based strictly on the context and aligned with the topic. Use clear, professional language. If the topic is:
                - **stocks** → summarize stock data or performance.
                - **economy** → explain macroeconomic data or events.
                - **news** → summarize recent relevant headlines.
                - **recommendation** → analyze stock trends (e.g. rising/falling prices, high/low volumes, recent gains or stability), and based on the context, suggest whether a stock appears to be a good investment. Provide reasoning using actual numbers (e.g. “This stock gained 5% today and shows strong volume, which indicates investor confidence”).
                topic: {topic}
                user question: {question} 
                context: {context}  
            """
        ),
]
)

generative_llm= ChatGoogleGenerativeAI(model=model_name, temperature=0)

generation_chain= prompt | generative_llm | StrOutputParser()