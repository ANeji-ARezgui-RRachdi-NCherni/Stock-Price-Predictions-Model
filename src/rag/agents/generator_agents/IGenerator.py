from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import dotenv
import os
from abc import ABC, abstractmethod

dotenv.load_dotenv()
model_name = os.environ.get("GENERATIVE_MODEL")

class IGenerator(ABC):
    """
    An absract class for the response generator agents.
    """

    def __init__(self,prompt, temperature: float = 0):
        self.prompt = prompt
        self.decision_chain = None
        self.generative_llm = ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
        self.__create_decision_chain()

    @abstractmethod
    def create_prompt(self) -> str:
        """
        Create a prompt based on the provided topic, question, and context.

        Args:
            topic (str): The topic of the question.
            question (str): The user's question.
            context (str): The context to base the response on.

        Returns:
            str: The generated prompt.
        """
        pass

    def __create_decision_chain(self) -> str:
        """
        Create the agent's decision chain.

        Args:.

        Returns:
            str: decision chain.
        """
        self.decision_chain =  self.prompt | self.generative_llm | StrOutputParser()


    def get_decision_chain(self) -> str:
        """
        Get the agent's decision chain.

        Returns:
            str: decision chain.
        """
        if self.decision_chain is None:
            raise ValueError("Decision chain has not been created yet.")
        return self.decision_chain