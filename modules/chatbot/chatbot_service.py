"""Service for the Chatbot module using LangChain and Google Gemini."""

import os
from typing import Dict, List
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory

from config.app_config import AppConfig
from .tools import search_order, get_recent_orders

# Dictionary to store session history
store: Dict[str, BaseChatMessageHistory] = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

class ChatbotService:
    """Service for handling chatbot interactions with tool calling and memory."""

    def __init__(self):
        if not AppConfig.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment configuration.")

        # Initialize the Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=AppConfig.google_api_key,
            temperature=0.7,
        )

        # Define tools
        self.tools = [search_order, get_recent_orders]

        # Define the prompt
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful assistant for Daraz, an e-commerce platform. "
                       "You can help users check their order status and answer general questions. "
                       "If a user asks about their recent or latest orders, use the 'get_recent_orders' tool. "
                       "If they provide an order ID, use the 'search_order' tool. "
                       "Be polite and professional."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)

        # Create the agent executor
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)

        # Wrap with message history
        self.with_message_history = RunnableWithMessageHistory(
            self.agent_executor,
            get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    async def generate_response(self, message: str, session_id: str) -> str:
        """
        Generate a response from the chatbot.

        Args:
            message: The user's message.
            session_id: The session identifier for memory.

        Returns:
            The chatbot's response.
        """
        try:
            config = {"configurable": {"session_id": session_id}}
            response = self.with_message_history.invoke(
                {"input": message},
                config=config
            )
            return response["output"]
        except Exception as e:
            return f"Error generating response: {str(e)}"

# Singleton instance
chatbot_service = ChatbotService()
