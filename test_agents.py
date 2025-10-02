#!/usr/bin/env python3
"""
Simple Test Script for Production-Grade Agent System

This script demonstrates the new agent architecture with a simple example.
"""

import asyncio
import json
import logging
from app.agents.main import AgentSystem
from app.agents.config import Environment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main test function."""
    print("🚀 Testing Production-Grade Agent System")
    print("=" * 50)
    
    try:
        # Initialize the agent system
        agent_system = AgentSystem(environment=Environment.DEVELOPMENT)
        await agent_system.initialize_agents()
        
        print(f"✅ Initialized {len(agent_system.agents)} agents:")
        for agent_name in agent_system.agents.keys():
            print(f"   - {agent_name}")
        
        # Test Market Analysis Agent
        print("\n📈 Testing Market Analysis Agent:")
        print("-" * 30)
        
        market_query = "What is the latest news on Microsoft? Is it worth investing in?"
        market_result = await agent_system.process_query(market_query, "market_analysis")
        
        print(f"Query: {market_query}")
        print(f"Response: {market_result['response'][:150]}...")
        print(f"Status: {market_result['status']}")
        
        # Test Portfolio Analysis Agent
        print("\n📊 Testing Portfolio Analysis Agent:")
        print("-" * 30)
        
        portfolio_data = {
            "holdings": {
                "AAPL": 0.30,
                "MSFT": 0.40,
                "GOOGL": 0.30
            },
            "period": "1y"
        }
        
        portfolio_query = f"Analyze portfolio performance: {json.dumps(portfolio_data)}"
        portfolio_result = await agent_system.process_query(portfolio_query, "portfolio_analysis")
        
        print(f"Query: {portfolio_query[:50]}...")
        print(f"Response: {portfolio_result['response'][:150]}...")
        print(f"Status: {portfolio_result['status']}")
        
        # Test Agent Status
        print("\n📋 Agent Status:")
        print("-" * 15)
        
        status = agent_system.get_agent_status()
        for agent_name, agent_status in status.items():
            print(f"{agent_name}: {agent_status['status']} ({len(agent_status['capabilities'])} capabilities)")
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
