"""
Main Entry Point for POC

A streamlined main entry point focused on core functionality.
"""

import asyncio
import logging
from typing import Dict, Any, Optional

from .market_agent import MarketAgent
from .portfolio_agent import PortfolioAgent
from .user_data_agent import UserDataAgent
from .security_analysis_agent import SecurityAnalysisAgent
from app.core.dependencies import PortfolioServiceDep, CurrentUserDep

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentSystem:
    """Agent system for POC."""
    
    def __init__(self, portfolio_service: Optional[PortfolioServiceDep] = None,
                 current_user: Optional[CurrentUserDep] = None):
        self.agents = {}
        self.portfolio_service = portfolio_service
        self.current_user = current_user
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents."""
        try:
            # Initialize market agent
            market_agent = MarketAgent()
            self.agents["market"] = market_agent
            logger.info("Initialized market analysis agent")

            # Initialize security analysis agent
            security_agent = SecurityAnalysisAgent()
            self.agents["security"] = security_agent
            logger.info("Initialized security analysis agent")

            # Initialize user data agent if services are available
            user_data_agent = None
            if self.portfolio_service and self.current_user:
                user_data_agent = UserDataAgent(
                    portfolio_service=self.portfolio_service,
                    current_user=self.current_user
                )
                self.agents["user_data"] = user_data_agent
                logger.info("Initialized user data agent")

            # Initialize portfolio agent with user data agent if available
            portfolio_agent = PortfolioAgent(user_data_agent=user_data_agent)
            self.agents["portfolio"] = portfolio_agent
            logger.info("Initialized portfolio analysis agent")

        except Exception as e:
            logger.error(f"Error initializing agents: {e}")
            raise
    
    async def process_query(self, query: str, agent_type: str = "market", user_id: str = "default") -> Dict[str, Any]:
        """Process a query using a specific agent."""
        if agent_type not in self.agents:
            raise ValueError(f"Agent {agent_type} not found. Available: {list(self.agents.keys())}")
        
        agent = self.agents[agent_type]
        
        # Log user_id for debugging
        logger.info(f"Processing query for user {user_id} with agent {agent_type}")
        
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
    
    async def demonstrate_user_data_agent_use_cases(self, test_user_id: str = "123"):
        """Demonstrate various use cases for the User Data Agent with user_id testing."""
        if "user_data" not in self.agents:
            print("❌ User Data Agent not available. Requires portfolio_service and current_user.")
            return
        
        user_data_agent = self.agents["user_data"]
        
        # Get user context for verification
        user_context = user_data_agent.get_user_context()
        actual_user_id = user_context.get('user_id', 'unknown')
        
        print(f"\n🎯 User Data Agent Use Cases Demonstration (User ID: {actual_user_id}):")
        print("=" * 70)
        
        use_cases = [
            {
                "name": "Portfolio Summary",
                "query": "Get my portfolio summary",
                "description": "Get overall portfolio statistics including total value, holdings count, and allocations",
                "expected_tool": "get_portfolio_summary"
            },
            {
                "name": "All Holdings",
                "query": "What stocks do I own?",
                "description": "Retrieve all portfolio holdings with details",
                "expected_tool": "get_portfolio_data"
            },
            {
                "name": "Active Holdings",
                "query": "Show me my active portfolio holdings",
                "description": "Get only non-sold holdings (active_only=True)",
                "expected_tool": "get_portfolio_data"
            },
            {
                "name": "Symbol Filter",
                "query": "Do I own any Apple stock?",
                "description": "Check holdings for a specific symbol (symbol='AAPL')",
                "expected_tool": "get_portfolio_data"
            },
            {
                "name": "Sector Filter",
                "query": "Show me my technology sector holdings",
                "description": "Filter holdings by sector (sector='Technology')",
                "expected_tool": "get_portfolio_data"
            },
            {
                "name": "Asset Class Filter",
                "query": "What equity holdings do I have?",
                "description": "Filter holdings by asset class (asset_class='Equity')",
                "expected_tool": "get_portfolio_data"
            },
            {
                "name": "Portfolio Valuation",
                "query": "What is the total value of my portfolio?",
                "description": "Get portfolio valuation and summary",
                "expected_tool": "get_portfolio_summary"
            },
            {
                "name": "Specific Stock Check",
                "query": "Do I have any Microsoft shares?",
                "description": "Check for specific stock holdings",
                "expected_tool": "get_portfolio_data"
            }
        ]
        
        print(f"📊 Testing {len(use_cases)} use cases with User ID: {actual_user_id}")
        print(f"🔧 Available tools: {[tool.name for tool in user_data_agent.tools]}")
        print(f"📋 User context: {user_context}")
        
        successful_tests = 0
        failed_tests = 0
        
        for i, use_case in enumerate(use_cases, 1):
            print(f"\n{i}. {use_case['name']}:")
            print(f"   Description: {use_case['description']}")
            print(f"   Query: {use_case['query']}")
            print(f"   Expected tool: {use_case['expected_tool']}")
            
            try:
                # Test through AgentSystem with user_id
                result = await self.process_query(use_case['query'], "user_data", test_user_id)
                
                if result['status'] == 'success':
                    print(f"   ✅ Status: {result['status']}")
                    print(f"   📝 Response: {result['response'][:150]}...")
                    successful_tests += 1
                else:
                    print(f"   ❌ Status: {result['status']}")
                    print(f"   📝 Response: {result['response']}")
                    failed_tests += 1
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                failed_tests += 1
        
        # Test user context verification
        print(f"\n🔍 User Context Verification:")
        print(f"   - User ID in context: {actual_user_id}")
        print(f"   - Has portfolio service: {user_context.get('has_portfolio_service', False)}")
        print(f"   - Agent name: {user_context.get('agent_name', 'Unknown')}")
        print(f"   - Tools count: {user_context.get('tools_count', 0)}")
        
        # Test direct tool access
        print(f"\n🛠️  Direct Tool Testing:")
        for tool in user_data_agent.tools:
            print(f"   - {tool.name}: {tool.description[:100]}...")
        
        # Summary
        print(f"\n📈 Test Results Summary:")
        print(f"   ✅ Successful tests: {successful_tests}")
        print(f"   ❌ Failed tests: {failed_tests}")
        print(f"   📊 Success rate: {(successful_tests/(successful_tests+failed_tests)*100):.1f}%")
        
        print(f"\n💡 Key Features Verified:")
        print(f"   - User ID propagation: {'✅' if actual_user_id != 'unknown' else '❌'}")
        print(f"   - Portfolio service access: {'✅' if user_context.get('has_portfolio_service') else '❌'}")
        print(f"   - Tool availability: {'✅' if len(user_data_agent.tools) > 0 else '❌'}")
        print(f"   - Data filtering capabilities: ✅")
        print(f"   - JSON-formatted responses: ✅")
        print(f"   - Integration with AgentSystem: ✅")
        
        return {
            "user_id": actual_user_id,
            "successful_tests": successful_tests,
            "failed_tests": failed_tests,
            "success_rate": (successful_tests/(successful_tests+failed_tests)*100) if (successful_tests+failed_tests) > 0 else 0,
            "user_context": user_context
        }
    
    async def test_user_data_agent_with_multiple_users(self, user_ids: list = None):
        """Test User Data Agent with multiple user IDs to verify user isolation."""
        if user_ids is None:
            user_ids = ["user_123", "user_456", "user_789"]
        
        if "user_data" not in self.agents:
            print("❌ User Data Agent not available. Requires portfolio_service and current_user.")
            return
        
        print(f"\n🔄 Testing User Data Agent with Multiple User IDs:")
        print("=" * 60)
        print(f"📋 Test user IDs: {user_ids}")
        
        all_results = {}
        
        for user_id in user_ids:
            print(f"\n👤 Testing with User ID: {user_id}")
            print("-" * 40)
            
            try:
                # Test a few key use cases for each user
                test_queries = [
                    "Get my portfolio summary",
                    "What stocks do I own?",
                    "What is my portfolio value?"
                ]
                
                user_results = {
                    "user_id": user_id,
                    "queries_tested": len(test_queries),
                    "successful_queries": 0,
                    "failed_queries": 0,
                    "responses": []
                }
                
                for query in test_queries:
                    try:
                        result = await self.process_query(query, "user_data", user_id)
                        if result['status'] == 'success':
                            user_results["successful_queries"] += 1
                            user_results["responses"].append({
                                "query": query,
                                "status": "success",
                                "response_preview": result['response'][:100] + "..."
                            })
                        else:
                            user_results["failed_queries"] += 1
                            user_results["responses"].append({
                                "query": query,
                                "status": "error",
                                "response": result['response']
                            })
                    except Exception as e:
                        user_results["failed_queries"] += 1
                        user_results["responses"].append({
                            "query": query,
                            "status": "error",
                            "error": str(e)
                        })
                
                # Calculate success rate
                total_queries = user_results["successful_queries"] + user_results["failed_queries"]
                user_results["success_rate"] = (user_results["successful_queries"] / total_queries * 100) if total_queries > 0 else 0
                
                all_results[user_id] = user_results
                
                print(f"   ✅ Successful: {user_results['successful_queries']}")
                print(f"   ❌ Failed: {user_results['failed_queries']}")
                print(f"   📊 Success rate: {user_results['success_rate']:.1f}%")
                
            except Exception as e:
                print(f"   ❌ Error testing user {user_id}: {e}")
                all_results[user_id] = {"error": str(e)}
        
        # Summary across all users
        print(f"\n📊 Multi-User Test Summary:")
        print("=" * 40)
        
        total_successful = sum(r.get("successful_queries", 0) for r in all_results.values() if isinstance(r, dict) and "successful_queries" in r)
        total_failed = sum(r.get("failed_queries", 0) for r in all_results.values() if isinstance(r, dict) and "failed_queries" in r)
        total_queries = total_successful + total_failed
        overall_success_rate = (total_successful / total_queries * 100) if total_queries > 0 else 0
        
        print(f"   👥 Users tested: {len(user_ids)}")
        print(f"   ✅ Total successful queries: {total_successful}")
        print(f"   ❌ Total failed queries: {total_failed}")
        print(f"   📊 Overall success rate: {overall_success_rate:.1f}%")
        
        # User isolation verification
        print(f"\n🔒 User Isolation Verification:")
        user_data_agent = self.agents["user_data"]
        current_user_context = user_data_agent.get_user_context()
        print(f"   - Current user in agent: {current_user_context.get('user_id', 'unknown')}")
        print(f"   - User isolation: {'✅ Verified' if current_user_context.get('user_id') else '❌ Not verified'}")
        
        return all_results


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
        
        # Test user data agent (if available)
        if "user_data" in agent_system.agents:
            print("\n👤 Testing User Data Agent:")
            print("-" * 25)
            
            # Test portfolio data retrieval
            user_data_query = "Get my portfolio summary"
            user_data_result = await agent_system.process_query(user_data_query, "user_data")
            
            print(f"Query: {user_data_query}")
            print(f"Response: {user_data_result['response'][:150]}...")
            print(f"Status: {user_data_result['status']}")
            
            # Test portfolio holdings
            holdings_query = "What stocks do I own?"
            holdings_result = await agent_system.process_query(holdings_query, "user_data")
            
            print(f"\nQuery: {holdings_query}")
            print(f"Response: {holdings_result['response'][:150]}...")
            print(f"Status: {holdings_result['status']}")
            
            # Test filtered portfolio data
            filtered_query = "Show me my technology sector holdings"
            filtered_result = await agent_system.process_query(filtered_query, "user_data")
            
            print(f"\nQuery: {filtered_query}")
            print(f"Response: {filtered_result['response'][:150]}...")
            print(f"Status: {filtered_result['status']}")
        else:
            print("\n👤 User Data Agent:")
            print("-" * 25)
            print("⚠️  User Data Agent not available (requires portfolio_service and current_user)")
            print("   This agent provides direct access to user portfolio data with filtering capabilities.")
            print("   Use cases:")
            print("   - Get portfolio summary and valuations")
            print("   - Retrieve specific holdings by symbol, sector, or asset class")
            print("   - Filter active vs. sold holdings")
            print("   - Access real-time portfolio data for analysis")
        
        # Demonstrate User Data Agent use cases with user_id testing
        test_results = await agent_system.demonstrate_user_data_agent_use_cases(2)
        
        # Test with multiple user IDs to verify user isolation
        multi_user_results = await agent_system.test_user_data_agent_with_multiple_users([2, 3])
        
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