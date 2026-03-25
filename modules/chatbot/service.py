"""Service for the Chatbot module using LangGraph and Google Gemini."""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

from config.app_config import AppConfig, ChatbotConfig
from utils.logger.logger import Logger
from .tools import (
    search_order,
    get_recent_orders,
    list_products,
    get_product_categories,
)

logger = Logger()

SYSTEM_PROMPT = (
    "You are a helpful assistant for Daraz, an e-commerce platform. "
    "You can help users check their order status, browse products, and answer general questions. "
    "If a user asks about their recent or latest orders, use the 'get_recent_orders' tool. "
    "If they provide an order ID, use the 'search_order' tool. "
    "If a user asks about products, what's available, or wants to browse by category, "
    "use the 'list_products' tool. You can filter by category if the user specifies one. "
    "If a user asks what product categories are available, use the 'get_product_categories' tool. "
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
        self.tools = [
            search_order,
            get_recent_orders,
            list_products,
            get_product_categories,
        ]

        # Create the ReAct agent (tool-calling) with persistent memory
        self.agent = create_agent(
            model=self.llm,
            tools=self.tools,
            checkpointer=self.memory,
            system_prompt=SystemMessage(content=SYSTEM_PROMPT),
        )

    @staticmethod
    def _extract_text(content) -> str:
        """Extract plain text from agent response content."""
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text" and "text" in part:
                        return part["text"]
                    if "text" in part:
                        return part["text"]
                if isinstance(part, str):
                    return part
        return str(content)

    async def generate_response(self, message: str, session_id: str) -> str:
        """
        Generate a response from the chatbot.

        Args:
            message: The user's message.
            session_id: The session identifier for memory.

        Returns:
            The chatbot's response.
        """

        logger.info(message=f"Generating response for session {session_id}")
        try:
            config = {"configurable": {"thread_id": session_id}}
            response = await self.agent.ainvoke(
                {"messages": [{"role": "user", "content": message}]},
                config=config,
            )

            raw_content = response["messages"][-1].content
            logger.info(
                message="Agent response received",
                content_type=type(raw_content).__name__,
            )

            return self._extract_text(raw_content)

        except Exception as e:
            logger.error(
                message="Error generating chatbot response",
                error_type=type(e).__name__,
                error=str(e),
                session_id=session_id,
            )
            return f"Error generating response: {str(e)}"


# Singleton instance
chatbot_service = ChatbotService()
