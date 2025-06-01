from .IGenerator import IGenerator
from langchain_core.prompts import ChatPromptTemplate


class NewsAgent(IGenerator):
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
        # table_instructions = """
        # Some of the retrieved information is presented in table format. When using information from tables:
        # 1. Present tabular data using proper markdown table formatting with headers, like this:
        #     | Column1 | Column2 | Column3 |
        #     |---------|---------|---------|
        #     | Value1  | Value2  | Value3  |
        # 2. Re-format the table structure to make it easier to read and understand
        # 3. If any new component is introduced during re-formatting of the table, mention it explicitly
        # 4. Clearly interpret the tabular data in your response
        # 5. Reference the relevant table when presenting specific data points
        # 6. If appropriate, summarize trends or patterns shown in the tables
        # 7. If only reference numbers are mentioned and you can fetch the corresponding values like research paper title or authors from the context, replace the reference numbers with the actual values
        # """
        # response_format_instructions = """Instructions:
        # 1. Answer the query based ONLY on the information provided in the context.
        # 2. If the context doesn't contain relevant information to answer the query, state: "I don't have enough information to answer this question based on the provided context."
        # 3. Do not use prior knowledge not contained in the context.
        # 5. Be concise and accurate.
        # 6. Provide a well-structured response with heading, sub-headings and tabular structure if required in markdown format based on retrieved knowledge. Keep the headings and sub-headings small sized.
        # 7. Only provide sections that are meaningful to have in a chatbot reply. For example, do not explicitly mention references.
        # 8. If values are involved, make sure to respond with perfect values present in context. Do not make up values.
        # 9. Do not repeat the question in the answer or response."""

        prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """You are a financial assistant specializing in analyzing and summarizing stock market news specifically related to the Tunisian economy. 
                            Your task is to carefully read given news articles, extract the key financial and economic insights relevant to Tunisia's stock market, 
                            and present a clear, concise summary that highlights the impact on investors and market trends.

                            # Steps

                            1. Thoroughly review the provided stock market news related to the Tunisian economy.
                            2. Identify major themes such as market movements, economic indicators, government policies, corporate earnings, and regional or global factors affecting Tunisia.
                            3. Analyze how these factors influence the Tunisian stock market and investor sentiment.
                            4. Summarize the information in a clear, structured way focusing on practical insights.

                            # Output Format

                            - Provide a well-organized summary in paragraph form.
                            - Provide a well-structured response with heading, sub-headings and tabular structure if required in markdown format based on retrieved knowledge. Keep the headings and sub-headings small sized.
                            - Use clear, professional financial language.
                            - Highlight key statistics or important dates if mentioned.
                            - Emphasize implications for investors and market outlook.
                            - If values are involved, make sure to respond with perfect values present in context. Do not make up values.
                            - Do not repeat the question in the answer or response.
                            - Do not start the response with "The answer is" or "Based on the context" similar phrases.

                            # Notes

                            - Ensure accuracy and relevance strictly pertaining to Tunisia's economy and stock market.
                            - Avoid unrelated financial information or speculation outside the Tunisian context. """),
                        
                        (
                        "human",
                        """
                        user question: {question} 
                        context: {context}  
                        """
                    ),
            ]
            )
        print("News Agent Prompt Created")
        return prompt

    