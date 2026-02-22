"""Service for the Chatbot module using LangGraph and Google Gemini."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

from config.app_config import AppConfig, ChatbotConfig
from .tools import search_order, get_recent_orders


SYSTEM_PROMPT = (
    "You are a helpful assistant for Daraz, an e-commerce platform. "
    "You can help users check their order status and answer general questions. "
    "If a user asks about their recent or latest orders, use the 'get_recent_orders' tool. "
    "If they provide an order ID, use the 'search_order' tool. "
    "Be polite and professional."
)


class ChatbotService:
    """Service for handling chatbot interactions with tool calling and memory."""

    def __init__(self):
        if not AppConfig.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment configuration.")

        # Initialize the Gemini model
        self.llm = ChatGoogleGenerativeAI(
            model=ChatbotConfig.model_name,
            google_api_key=AppConfig.google_api_key,
            temperature=0.7,
        )

        # In-memory checkpointer for per-session conversation history
        self.memory = MemorySaver()

        # Define tools
        self.tools = [search_order, get_recent_orders]

        # Create the ReAct agent (tool-calling) with persistent memory
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=self.memory,
            prompt=SystemMessage(content=SYSTEM_PROMPT),
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
            config = {"configurable": {"thread_id": session_id}}
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
            )
            # The last message in the response is the AI reply
            raw_response = response["messages"][-1].content
            response_dict = raw_response[0]

            return response_dict.get("text")

        except Exception as e:
            return f"Error generating response: {str(e)}"


# Singleton instance
chatbot_service = ChatbotService()
