from .IGenerator import IGenerator
from langchain_core.prompts import ChatPromptTemplate


class RecommenderAgent(IGenerator):
    def __init__(self):
        self.prompt = self.create_prompt()
        super().__init__(temperature=0)

    
    
    def create_prompt(self):
        """
        Create a prompt based on the provided topic, question, and context.
        
        Args:
            topic (str): The topic of the question.
            question (str): The user's question.
            context (str): The context to base the response on.
        
        Returns:
            str: The generated prompt.
        """
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
        return prompt

    