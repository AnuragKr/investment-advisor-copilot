#!/usr/bin/env python3
"""
Simple POC Test Script

A streamlined test script for the simplified agent system.
Automatically loads API keys from .env file.
"""

import asyncio
import json
from app.agents.main import AgentSystem


async def test_market_agent():
    """Test the market analysis agent."""
    print("📈 Testing Market Analysis Agent")
    print("=" * 35)
    
    agent_system = AgentSystem()
    
    # Test queries
    queries = [
        "What is the latest news on Apple?",
        "Analyze the technology sector performance",
        "Get stock information for Microsoft"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 30)
        
        try:
            result = await agent_system.process_query(query, "market")
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📊 Status: {result['status']}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_portfolio_agent():
    """Test the portfolio analysis agent."""
    print("\n📊 Testing Portfolio Analysis Agent")
    print("=" * 35)
    
    agent_system = AgentSystem()
    
    # Test portfolio data
    portfolio_data = {
        "holdings": {
            "AAPL": 0.30,
            "MSFT": 0.40,
            "GOOGL": 0.30
        }
    }
    
    # Test queries
    queries = [
        f"Analyze this portfolio: {json.dumps(portfolio_data)}",
        f"Assess the risk of this portfolio: {json.dumps(portfolio_data)}",
        f"Optimize this portfolio: {json.dumps(portfolio_data)}"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: {query[:50]}...")
        print("-" * 30)
        
        try:
            result = await agent_system.process_query(query, "portfolio")
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📊 Status: {result['status']}")
        except Exception as e:
            print(f"❌ Error: {e}")


async def test_agent_status():
    """Test agent status and capabilities."""
    print("\n📋 Testing Agent Status")
    print("=" * 25)
    
    agent_system = AgentSystem()
    
    # Get agent status
    status = agent_system.get_agent_status()
    
    print("Available agents:")
    for agent_type, agent_status in status.items():
        print(f"  • {agent_type}: {agent_status['name']}")
        print(f"    - Tools: {agent_status['tools_count']}")
        print(f"    - Model: {agent_status['model']}")


async def main():
    """Main test function."""
    print("🚀 Simplified Agent System - POC Test")
    print("=" * 45)
    
    try:
        # Run all tests
        await test_market_agent()
        await test_portfolio_agent()
        await test_agent_status()
        
        print("\n✅ All POC tests completed successfully!")
        print("\n💡 This simplified system is perfect for:")
        print("   - Proof of concept demonstrations")
        print("   - Quick prototyping")
        print("   - Core functionality testing")
        print("   - Easy deployment and maintenance")
        print("\n🔑 API Keys are automatically loaded from .env file")
        print("   - No need to set environment variables manually")
        print("   - Just create a .env file with your API keys")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
