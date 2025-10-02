"""
Market Analysis Agent for POC

A streamlined market analysis agent focused on core functionality.
"""

import logging
from typing import List
import requests
import yfinance as yf
from langchain_core.tools import tool

from .base import BaseAgent, AgentConfig
from app.config import agents_settings as config

logger = logging.getLogger(__name__)


class MarketAgent(BaseAgent):
    """Market analysis agent."""
    
    def __init__(self):
        agent_config = AgentConfig(
            name="Market Analysis Agent",
            description="Agent for market news and analysis",
            model_name="gpt-4o-mini",
            temperature=0.0,
            max_iterations=2,
            system_message="You are a market analysis agent. Provide clear, concise analysis of market data and news.",
            openai_api_key=config.OPENAI_API_KEY
        )
        super().__init__(agent_config)
    
    def _initialize_tools(self) -> List:
        """Initialize market analysis tools."""
        return [
            self._create_market_news_tool(),
            self._create_sector_performance_tool(),
            self._create_stock_info_tool()
        ]
    
    def _get_system_message(self) -> str:
        """Get the system message for market analysis."""
        return """You are a market analysis agent specialized in financial news and market data.

Your capabilities:
- Fetch latest financial news
- Analyze sector performance
- Get stock information

Guidelines:
- Provide clear, concise analysis
- Include relevant metrics and data
- Focus on actionable insights
- Keep responses professional but accessible"""
    
    def _create_market_news_tool(self):
        """Create the market news tool."""
        
        @tool
        def fetch_market_news(query: str) -> str:
            """Fetch latest financial news using NewsAPI.
            
            Args:
                query: Search query for financial news (e.g., "Apple", "tech stocks")
            
            Returns:
                String containing latest news headlines
            """
            try:
                url = f"https://newsapi.org/v2/everything?q={query}&apiKey={config.NEWS_API_KEY}&sortBy=publishedAt&pageSize=3"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                if "articles" in data and data["articles"]:
                    news_items = []
                    for article in data["articles"][:3]:
                        title = article.get("title", "No title")
                        description = article.get("description", "No description")
                        news_items.append(f"• {title}\n  {description}")
                    
                    return f"Latest news for '{query}':\n\n" + "\n\n".join(news_items)
                else:
                    return f"No recent news found for '{query}'"
                    
            except Exception as e:
                logger.error(f"Error fetching market news: {e}")
                return f"Error fetching news for '{query}': {str(e)}"
        
        return fetch_market_news
    
    def _create_sector_performance_tool(self):
        """Create the sector performance tool."""
        
        @tool
        def analyze_sector_performance(sector: str) -> str:
            """Analyze sector performance using ETF data.
            
            Args:
                sector: Sector to analyze (e.g., "tech", "finance", "healthcare")
            
            Returns:
                String containing sector performance analysis
            """
            try:
                # Sector to ETF mapping
                sector_mapping = {
                    "tech": "XLK",
                    "technology": "XLK", 
                    "finance": "XLF",
                    "financial": "XLF",
                    "healthcare": "XLV",
                    "health": "XLV",
                    "energy": "XLE",
                    "utilities": "XLU"
                }
                
                ticker = sector_mapping.get(sector.lower(), "SPY")
                
                # Get historical data
                stock = yf.Ticker(ticker)
                hist = stock.history(period="1y")
                
                if hist.empty:
                    return f"No data available for {sector} sector"
                
                # Calculate performance
                current_price = hist["Close"][-1]
                ytd_change = ((current_price - hist["Close"][0]) / hist["Close"][0]) * 100
                
                # Get additional info
                info = stock.info
                market_cap = info.get("marketCap", "N/A")
                
                return f"""Sector Performance: {sector.upper()} ({ticker})

📊 Performance:
• Current Price: ${current_price:.2f}
• YTD Change: {ytd_change:+.2f}%
• Market Cap: {market_cap:,} (if available)

💡 Analysis:
{'Strong performance' if ytd_change > 10 else 'Moderate performance' if ytd_change > 0 else 'Declining performance'} year-to-date."""
                
            except Exception as e:
                logger.error(f"Error analyzing sector performance: {e}")
                return f"Error analyzing {sector} sector: {str(e)}"
        
        return analyze_sector_performance
    
    def _create_stock_info_tool(self):
        """Create the stock information tool."""
        
        @tool
        def get_stock_info(ticker: str) -> str:
            """Get basic stock information.
            
            Args:
                ticker: Stock ticker symbol (e.g., "AAPL", "MSFT")
            
            Returns:
                String containing stock information
            """
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1mo")
                
                if hist.empty:
                    return f"No data available for {ticker}"
                
                current_price = hist["Close"][-1]
                price_change = ((current_price - hist["Close"][0]) / hist["Close"][0]) * 100
                
                return f"""Stock Information: {ticker.upper()}

📊 Current Data:
• Price: ${current_price:.2f}
• 1-Month Change: {price_change:+.2f}%
• Market Cap: {info.get('marketCap', 'N/A'):,}
• P/E Ratio: {info.get('trailingPE', 'N/A')}
• 52-Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
• 52-Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}

💡 Analysis:
{'Positive momentum' if price_change > 5 else 'Stable performance' if price_change > -5 else 'Negative momentum'} in the past month."""
                
            except Exception as e:
                logger.error(f"Error getting stock info: {e}")
                return f"Error getting info for {ticker}: {str(e)}"
        
        return get_stock_info
