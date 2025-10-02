"""
Example: Production-Grade Agent System Demo

This script demonstrates the new production-grade agent architecture
with inter-agent communication, configuration management, and scalability.
"""

import asyncio
import json
import logging
import os
from typing import Dict, Any

from dotenv import load_dotenv

# Import the new agent system
from app.agents.main import AgentSystem
from app.agents.config import Environment

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_market_analysis():
    """Demonstrate market analysis agent capabilities."""
    print("\n" + "="*80)
    print("DEMO: Market Analysis Agent")
    print("="*80)
    
    agent_system = AgentSystem(environment=Environment.DEVELOPMENT)
    await agent_system.initialize_agents()
    
    # Test market analysis queries
    queries = [
        "What is the latest news on Microsoft? Is it worth investing in?",
        "Analyze the technology sector performance",
        "Get SEC filings for Apple Inc.",
        "What are the current market trends in AI and machine learning?"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 60)
        
        try:
            result = await agent_system.process_query(query, "market_analysis")
            print(f"✅ Response: {result['response'][:200]}...")
            print(f"📊 Status: {result['status']}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def demo_portfolio_analysis():
    """Demonstrate portfolio analysis agent capabilities."""
    print("\n" + "="*80)
    print("DEMO: Portfolio Analysis Agent")
    print("="*80)
    
    agent_system = AgentSystem(environment=Environment.DEVELOPMENT)
    await agent_system.initialize_agents()
    
    # Sample portfolio data
    portfolio_data = {
        "holdings": {
            "AAPL": 0.30,
            "MSFT": 0.40,
            "GOOGL": 0.30
        },
        "period": "1y"
    }
    
    # Test portfolio analysis queries
    queries = [
        f"Analyze portfolio performance: {json.dumps(portfolio_data)}",
        f"Calculate risk metrics for: {json.dumps(portfolio_data)}",
        f"Optimize portfolio allocation for: {json.dumps(portfolio_data)}",
        f"Generate comprehensive performance report for: {json.dumps(portfolio_data)}"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query[:50]}...")
        print("-" * 60)
        
        try:
            result = await agent_system.process_query(query, "portfolio_analysis")
            print(f"✅ Response: {result['response'][:200]}...")
            print(f"📊 Status: {result['status']}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def demo_inter_agent_communication():
    """Demonstrate inter-agent communication."""
    print("\n" + "="*80)
    print("DEMO: Inter-Agent Communication")
    print("="*80)
    
    agent_system = AgentSystem(environment=Environment.DEVELOPMENT)
    await agent_system.initialize_agents()
    
    # Get agents
    market_agent = agent_system.agents.get("market_analysis")
    portfolio_agent = agent_system.agents.get("portfolio_analysis")
    
    if market_agent and portfolio_agent:
        print("\n🤝 Testing agent communication...")
        
        # Market agent sends market data to portfolio agent
        await market_agent.send_message_to_agent(
            portfolio_agent.agent_id,
            "Market update: Tech sector showing strong performance with 15% YTD gains",
            message_type="broadcast"
        )
        
        # Portfolio agent responds with portfolio insights
        await portfolio_agent.send_message_to_agent(
            market_agent.agent_id,
            "Portfolio analysis: Current tech allocation at 70%, considering rebalancing",
            message_type="response"
        )
        
        print("✅ Inter-agent communication successful")
    else:
        print("❌ Required agents not available")


async def demo_agent_status_monitoring():
    """Demonstrate agent status monitoring."""
    print("\n" + "="*80)
    print("DEMO: Agent Status Monitoring")
    print("="*80)
    
    agent_system = AgentSystem(environment=Environment.DEVELOPMENT)
    await agent_system.initialize_agents()
    
    # Get status of all agents
    status = agent_system.get_agent_status()
    
    print("\n📊 Agent Status Report:")
    print("-" * 40)
    
    for agent_name, agent_status in status.items():
        print(f"Agent: {agent_name}")
        print(f"  Status: {agent_status['status']}")
        print(f"  Capabilities: {', '.join(agent_status['capabilities'])}")
        print(f"  Tools Count: {agent_status['tools_count']}")
        print(f"  Last Update: {agent_status['timestamp']}")
        print()


async def demo_scalability():
    """Demonstrate system scalability."""
    print("\n" + "="*80)
    print("DEMO: System Scalability")
    print("="*80)
    
    agent_system = AgentSystem(environment=Environment.DEVELOPMENT)
    await agent_system.initialize_agents()
    
    # Simulate multiple concurrent queries
    queries = [
        "Analyze Apple stock performance",
        "Get latest tech sector news",
        "Calculate portfolio risk metrics",
        "Optimize portfolio allocation",
        "Generate performance report"
    ]
    
    print(f"\n🚀 Processing {len(queries)} concurrent queries...")
    
    # Process queries concurrently
    tasks = []
    for i, query in enumerate(queries):
        agent_name = "market_analysis" if i % 2 == 0 else "portfolio_analysis"
        task = agent_system.process_query(query, agent_name)
        tasks.append(task)
    
    # Wait for all tasks to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"✅ Completed {len(results)} queries")
    
    # Show results summary
    successful = sum(1 for r in results if not isinstance(r, Exception))
    failed = len(results) - successful
    
    print(f"📊 Results: {successful} successful, {failed} failed")


async def main():
    """Main demo function."""
    print("🚀 Production-Grade Agent System Demo")
    print("="*80)
    
    try:
        # Run all demos
        await demo_market_analysis()
        await demo_portfolio_analysis()
        await demo_inter_agent_communication()
        await demo_agent_status_monitoring()
        await demo_scalability()
        
        print("\n" + "="*80)
        print("✅ All demos completed successfully!")
        print("="*80)
        
    except Exception as e:
        logger.error(f"Error in demo: {e}")
        print(f"❌ Demo failed: {e}")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
