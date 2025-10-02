"""
Main Entry Point for POC

A streamlined main entry point focused on core functionality.
"""

import asyncio
import logging
from typing import Dict, Any

from .market_agent import MarketAgent
from .portfolio_agent import PortfolioAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentSystem:
    """Agent system for POC."""
    
    def __init__(self):
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents."""
        try:
            # Initialize market agent
            market_agent = MarketAgent()
            self.agents["market"] = market_agent
            logger.info("Initialized market analysis agent")
            
            # Initialize portfolio agent
            portfolio_agent = PortfolioAgent()
            self.agents["portfolio"] = portfolio_agent
            logger.info("Initialized portfolio analysis agent")
            
        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
            raise
    
    async def process_query(self, query: str, agent_type: str = "market") -> Dict[str, Any]:
        """Process a query using a specific agent."""
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type} not found. Available: {list(self.agents.keys())}")
        
        agent = self.agents[agent_type]
        return await agent.process_query(query)
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents."""
        status = {}
        for agent_type, agent in self.agents.items():
            status[agent_type] = agent.get_status()
        return status
    
    def list_agents(self) -> list:
        """List all available agents."""
        return list(self.agents.keys())


async def main():
    """Main entry point for the agent system."""
    try:
        print("🚀 Agent System - POC")
        print("=" * 30)
        
        # Initialize the system
        agent_system = AgentSystem()
        
        print(f"✅ Initialized {len(agent_system.agents)} agents:")
        for agent_type in agent_system.list_agents():
            print(f"   - {agent_type}")
        
        # Test market agent
        print("\n📈 Testing Market Agent:")
        print("-" * 25)
        
        market_query = "What is the latest news on Microsoft? Is it worth investing in?"
        market_result = await agent_system.process_query(market_query, "market")
        
        print(f"Query: {market_query}")
        print(f"Response: {market_result['response'][:150]}...")
        print(f"Status: {market_result['status']}")
        
        # Test portfolio agent
        print("\n📊 Testing Portfolio Agent:")
        print("-" * 25)
        
        portfolio_data = '{"holdings": {"AAPL": 0.30, "MSFT": 0.40, "GOOGL": 0.30}}'
        portfolio_query = f"Analyze this portfolio: {portfolio_data}"
        portfolio_result = await agent_system.process_query(portfolio_query, "portfolio")
        
        print(f"Query: {portfolio_query[:50]}...")
        print(f"Response: {portfolio_result['response'][:150]}...")
        print(f"Status: {portfolio_result['status']}")
        
        # Show agent status
        print("\n📋 Agent Status:")
        print("-" * 15)
        
        status = agent_system.get_agent_status()
        for agent_type, agent_status in status.items():
            print(f"{agent_type}: {agent_status['name']} ({agent_status['tools_count']} tools)")
        
        print("\n✅ POC test completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())