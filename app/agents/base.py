"""
Base Agent Architecture

A streamlined version focused on core functionality for proof of concept.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.graph import MessagesState, StateGraph, END
from langgraph.prebuilt import ToolNode

from app.config import agents_settings as config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AgentConfig:
    """Configuration for agents."""
    name: str
    description: str = ""
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.0
    max_iterations: int = 2
    system_message: str = ""
    openai_api_key: str = ""


class BaseAgent(ABC):
    """Base class for AI agents."""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.llm = ChatOpenAI(
            model=config.model_name,
            temperature=config.temperature,
            api_key=config.openai_api_key
        )
        self.tools = self._initialize_tools()
        
        # Bind tools to LLM if tools are available
        if self.tools:
            self.llm = self.llm.bind_tools(self.tools)
        
        self.graph = self._build_graph()
        
        logger.info(f"Initialized agent: {self.name}")
    
    @abstractmethod
    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize tools specific to this agent."""
        pass
    
    @abstractmethod
    def _get_system_message(self) -> str:
        """Get the system message for this agent."""
        pass
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph for this agent."""
        graph = StateGraph(MessagesState)
        
        # Add reasoning node
        graph.add_node("reasoning", self._reasoning_node)
        graph.set_entry_point("reasoning")
        
        # Add tool node if tools are available
        if self.tools:
            tool_node = ToolNode(self.tools)
            graph.add_node("tools", tool_node)
            
            # Add conditional edges
            graph.add_conditional_edges(
                "reasoning",
                self._should_continue,
                {
                    END: END,
                    "tools": "tools"
                }
            )
            graph.add_edge("tools", END)  # End after tools, don't loop back
        else:
            graph.add_edge("reasoning", END)
        
        return graph.compile()
    
    async def _reasoning_node(self, state: MessagesState) -> MessagesState:
        """Reasoning node implementation."""
        try:
            system_message = {"role": "system", "content": self._get_system_message()}
            messages = [system_message] + state["messages"]
            
            response = await self.llm.ainvoke(messages)
            return {"messages": [response]}
        except Exception as e:
            logger.error(f"Error in reasoning node: {e}")
            error_message = AIMessage(content=f"Error: {str(e)}")
            return {"messages": [error_message]}
    
    def _should_continue(self, state: MessagesState) -> str:
        """Determine if the agent should continue or end."""
        if not state["messages"]:
            return END
        
        last_message = state["messages"][-1]
        
        # Check if the last message has tool calls
        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
            return "tools"
        
        return END
    
    async def process_query(self, query: str) -> Dict[str, Any]:
        """Process a query using the agent."""
        try:
            # Create initial message
            initial_message = HumanMessage(content=query)
            
            # Process through the graph asynchronously
            result = await self.graph.ainvoke(
                {"messages": [initial_message]},
                config={"recursion_limit": 10}
            )
            
            return {
                "agent_name": self.name,
                "query": query,
                "response": result["messages"][-1].content,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "agent_name": self.name,
                "query": query,
                "response": f"Error: {str(e)}",
                "status": "error"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "name": self.name,
            "tools_count": len(self.tools),
            "model": self.config.model_name
        }
