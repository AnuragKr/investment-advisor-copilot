"""
Security Analysis Agent - POC Version

Minimal technical analysis agent with essential indicators: RSI, Moving Averages, MACD.
"""

import logging
import yfinance as yf
import pandas_ta as ta
import pandas as pd
from typing import List
from langchain_core.tools import tool

from .base import BaseAgent, AgentConfig
from app.config import agents_settings as config

logger = logging.getLogger(__name__)


class SecurityAnalysisAgent(BaseAgent):
    """Minimal security analysis agent for POC."""

    def __init__(self):
        agent_config = AgentConfig(
            name="Security Analysis Agent",
            description="Agent for basic technical analysis (RSI, Moving Averages, MACD)",
            model_name="gpt-4o-mini",
            temperature=0.0,
            max_iterations=2,
            system_message="You are a security analysis agent for basic technical indicators.",
            openai_api_key=config.OPENAI_API_KEY
        )
        super().__init__(agent_config)

    def _initialize_tools(self) -> List:
        """Initialize minimal security analysis tools."""
        return [
            self._create_analyze_security_tool()
        ]

    def _get_system_message(self) -> str:
        """Get the system message for security analysis."""
        return """You are a security analysis agent for basic technical analysis.

Your capabilities:
- Calculate RSI (Relative Strength Index)
- Analyze Moving Averages (SMA_50, SMA_200)
- Compute MACD (Moving Average Convergence Divergence)
- Provide basic trading signals

Available tool:
- analyze_security(): Basic technical analysis for a security

Guidelines:
- Provide clear, simple technical analysis
- Focus on key indicators: RSI, Moving Averages, MACD
- Give basic buy/sell/neutral signals
- Keep responses concise and actionable"""

    def _create_analyze_security_tool(self):
        """Create tool for basic security analysis."""
        
        @tool
        async def analyze_security(ticker: str, period: str = "6mo") -> str:
            """Perform basic technical analysis on a security.
            
            Args:
                ticker: Stock symbol (e.g., "AAPL", "MSFT", "NVDA")
                period: Time period for data (default: "6mo")
            
            Returns:
                JSON string containing basic technical indicators and signal
            """
            try:
                # Download historical price data
                df = yf.download(ticker, period=period, progress=False)
                
                if df.empty:
                    return f"Error: No data found for ticker {ticker}"
                
                # Compute basic technical indicators
                df["RSI"] = ta.rsi(df["Close"], length=14)
                df["SMA_50"] = ta.sma(df["Close"], length=50)
                df["SMA_200"] = ta.sma(df["Close"], length=200)
                
                # MACD
                macd_data = ta.macd(df["Close"], fast=12, slow=26, signal=9)
                if macd_data is not None and not macd_data.empty:
                    df["MACD"] = macd_data["MACD_12_26_9"]
                    df["MACD_signal"] = macd_data["MACDs_12_26_9"]
                
                # Get latest values safely
                latest = df.iloc[-1]
                current_price = self._safe_float(latest["Close"])
                
                # Handle case where latest is a Series
                if hasattr(latest, 'iloc'):
                    current_price = self._safe_float(latest["Close"].iloc[0])
                else:
                    current_price = self._safe_float(latest["Close"])
                
                # Extract indicator values safely
                if hasattr(latest, 'iloc'):
                    rsi_value = self._safe_float(latest["RSI"].iloc[0]) if "RSI" in latest else None
                    sma_50 = self._safe_float(latest["SMA_50"].iloc[0]) if "SMA_50" in latest else None
                    sma_200 = self._safe_float(latest["SMA_200"].iloc[0]) if "SMA_200" in latest else None
                    macd = self._safe_float(latest["MACD"].iloc[0]) if "MACD" in latest else None
                    macd_signal = self._safe_float(latest["MACD_signal"].iloc[0]) if "MACD_signal" in latest else None
                else:
                    rsi_value = self._safe_float(latest["RSI"]) if "RSI" in latest else None
                    sma_50 = self._safe_float(latest["SMA_50"]) if "SMA_50" in latest else None
                    sma_200 = self._safe_float(latest["SMA_200"]) if "SMA_200" in latest else None
                    macd = self._safe_float(latest["MACD"]) if "MACD" in latest else None
                    macd_signal = self._safe_float(latest["MACD_signal"]) if "MACD_signal" in latest else None
                
                # Generate basic signal
                signal = self._generate_signal(rsi_value, current_price, sma_50, macd, macd_signal)
                
                result = {
                    "ticker": ticker.upper(),
                    "current_price": current_price,
                    "indicators": {
                        "RSI": rsi_value,
                        "SMA_50": sma_50,
                        "SMA_200": sma_200,
                        "MACD": macd,
                        "MACD_signal": macd_signal
                    },
                    "signal": signal
                }
                
                import json
                return json.dumps(result, default=str)
                
            except Exception as e:
                logger.error(f"Error analyzing security {ticker}: {e}")
                return f"Error analyzing security {ticker}: {str(e)}"
        
        return analyze_security
    
    def _safe_float(self, value):
        """Safely convert pandas value to float."""
        if value is None or pd.isna(value):
            return None
        try:
            if hasattr(value, 'iloc'):
                scalar = value.iloc[0]
                return float(scalar) if pd.notna(scalar) else None
            return float(value) if pd.notna(value) else None
        except (ValueError, TypeError, AttributeError):
            return None
    
    def _generate_signal(self, rsi, price, sma_50, macd, macd_signal):
        """Generate basic buy/sell/neutral signal."""
        signals = []
        
        # RSI signal
        if rsi is not None:
            if rsi < 30:
                signals.append("BUY (RSI oversold)")
            elif rsi > 70:
                signals.append("SELL (RSI overbought)")
            else:
                signals.append("NEUTRAL (RSI normal)")
        
        # Moving average signal
        if price is not None and sma_50 is not None:
            if price > sma_50:
                signals.append("BUY (Price above SMA50)")
            else:
                signals.append("SELL (Price below SMA50)")
        
        # MACD signal
        if macd is not None and macd_signal is not None:
            if macd > macd_signal:
                signals.append("BUY (MACD bullish)")
            else:
                signals.append("SELL (MACD bearish)")
        
        # Count signals
        buy_count = sum(1 for s in signals if "BUY" in s)
        sell_count = sum(1 for s in signals if "SELL" in s)
        
        if buy_count > sell_count:
            return "BULLISH"
        elif sell_count > buy_count:
            return "BEARISH"
        else:
            return "NEUTRAL"