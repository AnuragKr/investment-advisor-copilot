"""
Portfolio Analysis Agent for POC

A streamlined portfolio analysis agent focused on core functionality.
"""

import logging
from typing import List
import json
from langchain_core.tools import tool

from .base import BaseAgent, AgentConfig
from app.config import agents_settings as config

logger = logging.getLogger(__name__)


class PortfolioAgent(BaseAgent):
    """Portfolio analysis agent."""
    
    def __init__(self):
        agent_config = AgentConfig(
            name="Portfolio Analysis Agent",
            description="Agent for portfolio analysis and risk assessment",
            model_name="gpt-4o-mini",
            temperature=0.0,
            max_iterations=2,
            system_message="You are a portfolio analysis agent. Provide clear, concise portfolio analysis and recommendations.",
            openai_api_key=config.OPENAI_API_KEY
        )
        super().__init__(agent_config)
    
    def _initialize_tools(self) -> List:
        """Initialize portfolio analysis tools."""
        return [
            self._create_portfolio_analysis_tool(),
            self._create_risk_assessment_tool(),
            self._create_optimization_tool()
        ]
    
    def _get_system_message(self) -> str:
        """Get the system message for portfolio analysis."""
        return """You are a portfolio analysis agent specialized in portfolio management and risk assessment.

Your capabilities:
- Analyze portfolio performance
- Assess portfolio risk
- Provide optimization recommendations

Guidelines:
- Provide clear, data-driven analysis
- Include specific metrics and recommendations
- Focus on actionable insights
- Keep responses professional but accessible"""
    
    def _create_portfolio_analysis_tool(self):
        """Create the portfolio analysis tool."""
        
        @tool
        def analyze_portfolio(portfolio_data: str) -> str:
            """Analyze portfolio performance.
            
            Args:
                portfolio_data: JSON string with portfolio holdings
                Format: {"holdings": {"AAPL": 0.3, "MSFT": 0.4, "GOOGL": 0.3}}
            
            Returns:
                String containing portfolio analysis
            """
            try:
                data = json.loads(portfolio_data)
                holdings = data.get("holdings", {})
                
                if not holdings:
                    return "Error: No portfolio holdings provided"
                
                # Calculate basic metrics
                total_weight = sum(holdings.values())
                num_holdings = len(holdings)
                max_weight = max(holdings.values())
                
                # Simulate performance analysis
                analysis = f"""Portfolio Analysis

📊 Portfolio Composition:
• Total Holdings: {num_holdings}
• Total Weight: {total_weight:.1%}
• Largest Position: {max_weight:.1%}

📈 Performance Metrics (Simulated):
• Total Return: +12.5%
• Volatility: 18.2%
• Sharpe Ratio: 0.69
• Maximum Drawdown: -8.3%

💡 Analysis:
• {'Well diversified' if num_holdings >= 5 else 'Concentrated'} portfolio
• {'Balanced' if max_weight <= 0.3 else 'Top-heavy'} allocation
• Risk level: {'Moderate' if max_weight <= 0.4 else 'High'}

🎯 Recommendations:
• {'Consider adding more positions' if num_holdings < 5 else 'Good diversification'}
• {'Reduce largest position' if max_weight > 0.4 else 'Allocation looks balanced'}"""
                
                return analysis
                
            except json.JSONDecodeError:
                return "Error: Invalid JSON format for portfolio data"
            except Exception as e:
                logger.error(f"Error analyzing portfolio: {e}")
                return f"Error analyzing portfolio: {str(e)}"
        
        return analyze_portfolio
    
    def _create_risk_assessment_tool(self):
        """Create the risk assessment tool."""
        
        @tool
        def assess_portfolio_risk(portfolio_data: str) -> str:
            """Assess portfolio risk.
            
            Args:
                portfolio_data: JSON string with portfolio holdings
            
            Returns:
                String containing risk assessment
            """
            try:
                data = json.loads(portfolio_data)
                holdings = data.get("holdings", {})
                
                if not holdings:
                    return "Error: No portfolio holdings provided"
                
                # Calculate risk metrics
                num_holdings = len(holdings)
                max_weight = max(holdings.values())
                top_3_weight = sum(sorted(holdings.values(), reverse=True)[:3])
                
                # Risk assessment
                risk_level = "Low"
                if max_weight > 0.4 or num_holdings < 3:
                    risk_level = "High"
                elif max_weight > 0.3 or num_holdings < 5:
                    risk_level = "Medium"
                
                assessment = f"""Portfolio Risk Assessment

🔍 Risk Analysis:
• Number of Holdings: {num_holdings}
• Largest Position: {max_weight:.1%}
• Top 3 Positions: {top_3_weight:.1%}

📊 Risk Metrics:
• Concentration Risk: {'High' if max_weight > 0.4 else 'Medium' if max_weight > 0.3 else 'Low'}
• Diversification: {'Poor' if num_holdings < 3 else 'Fair' if num_holdings < 5 else 'Good'}
• Overall Risk Level: {risk_level}

⚠️ Risk Factors:
• {'High concentration in top positions' if max_weight > 0.4 else 'Moderate concentration'}
• {'Limited diversification' if num_holdings < 5 else 'Good diversification'}
• {'Consider adding defensive assets' if risk_level == 'High' else 'Risk level acceptable'}

💡 Recommendations:
• {'Reduce largest position' if max_weight > 0.4 else 'Allocation looks balanced'}
• {'Add more positions' if num_holdings < 5 else 'Diversification is good'}
• {'Consider bonds or defensive stocks' if risk_level == 'High' else 'Current risk level is acceptable'}"""
                
                return assessment
                
            except json.JSONDecodeError:
                return "Error: Invalid JSON format for portfolio data"
            except Exception as e:
                logger.error(f"Error assessing risk: {e}")
                return f"Error assessing risk: {str(e)}"
        
        return assess_portfolio_risk
    
    def _create_optimization_tool(self):
        """Create the portfolio optimization tool."""
        
        @tool
        def optimize_portfolio(portfolio_data: str) -> str:
            """Optimize portfolio allocation.
            
            Args:
                portfolio_data: JSON string with current portfolio holdings
            
            Returns:
                String containing optimization recommendations
            """
            try:
                data = json.loads(portfolio_data)
                holdings = data.get("holdings", {})
                
                if not holdings:
                    return "Error: No portfolio holdings provided"
                
                # Simple optimization logic
                current_holdings = list(holdings.keys())
                current_weights = list(holdings.values())
                
                # Suggest optimized allocation
                optimized_weights = [w * 0.9 for w in current_weights]  # Reduce current positions
                cash_allocation = 1 - sum(optimized_weights)
                
                optimization = f"""Portfolio Optimization

📊 Current vs. Optimized Allocation:

Current Portfolio:
"""
                for ticker, weight in holdings.items():
                    optimization += f"• {ticker}: {weight:.1%}\n"
                
                optimization += f"""
Optimized Portfolio:
"""
                for i, ticker in enumerate(current_holdings):
                    optimization += f"• {ticker}: {optimized_weights[i]:.1%}\n"
                
                if cash_allocation > 0:
                    optimization += f"• Cash: {cash_allocation:.1%}\n"
                
                optimization += f"""
📈 Expected Improvements:
• Better diversification
• Reduced concentration risk
• Improved risk-adjusted returns
• More flexibility for opportunities

🔄 Implementation:
• Gradual rebalancing recommended
• Consider transaction costs
• Monitor performance regularly
• Review quarterly

💡 Next Steps:
• Implement changes gradually
• Monitor market conditions
• Adjust based on performance
• Consider new opportunities"""
                
                return optimization
                
            except json.JSONDecodeError:
                return "Error: Invalid JSON format for portfolio data"
            except Exception as e:
                logger.error(f"Error optimizing portfolio: {e}")
                return f"Error optimizing portfolio: {str(e)}"
        
        return optimize_portfolio
