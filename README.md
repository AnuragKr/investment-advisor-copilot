## 💹 Investment Advisory Co-Pilot

A multi-agent AI system that supports investment advisors by analyzing portfolios, assessing risks, researching markets, and generating intelligent recommendations.
The project leverages LangGraph (or similar orchestration frameworks) to coordinate specialized agents that collaborate to answer both simple portfolio questions and complex financial analysis queries.

## 📌 Overview

This project demonstrates how AI agents can automate and enhance the investment advisory process. Instead of relying on manual research and analysis, the system coordinates multiple specialized agents to:

+ Analyze market conditions, news, and sector performance
+ Perform technical and statistical analysis of securities
+ Assess portfolio risks and client-specific tolerance
+ Recommend optimal asset allocations and strategies

The result is a co-pilot for advisors that can handle natural language queries, synthesize complex data, and deliver consistent, data-backed recommendations.

## 🏗️ System Architecture

### Agent Roles and Responsibilities

The system consists of 4 specialized agents, each with distinct roles and responsibilities:

#### 1. **Market Analysis Agent** (`market`)
- **Primary Role**: Market data analysis and news aggregation
- **Responsibilities**:
  - Fetch latest financial news using NewsAPI
  - Analyze sector performance and market trends
  - Provide stock price information and market insights
  - Monitor market conditions and volatility
- **Tools**:
  - `fetch_market_news()`: Get latest financial news
  - `fetch_sector_performance()`: Analyze sector performance
  - `fetch_stock_price()`: Get current stock prices
  - `fetch_market_trends()`: Analyze market trends
  - `fetch_top_performing_stocks()`: Identify top performers

#### 2. **Security Analysis Agent** (`security`)
- **Primary Role**: Technical analysis and trading signals
- **Responsibilities**:
  - Calculate technical indicators (RSI, Moving Averages, MACD)
  - Generate buy/sell/neutral trading signals
  - Provide technical analysis for individual securities
  - Assess momentum and trend strength
- **Tools**:
  - `analyze_security()`: Complete technical analysis with indicators and signals

#### 3. **User Data Agent** (`user_data`)
- **Primary Role**: User portfolio data access and management
- **Responsibilities**:
  - Access user portfolio holdings from database
  - Provide portfolio summaries and statistics
  - Filter and query user-specific data
  - Ensure data privacy and user isolation
- **Tools**:
  - `get_portfolio_data()`: Retrieve user portfolio holdings
  - `get_portfolio_summary()`: Get portfolio statistics and summary

#### 4. **Portfolio Analysis Agent** (`portfolio`)
- **Primary Role**: Portfolio analysis and investment recommendations
- **Responsibilities**:
  - Analyze portfolio performance and risk
  - Provide investment recommendations
  - Assess portfolio optimization opportunities
  - Generate risk assessments and diversification analysis
- **Tools**:
  - `analyze_portfolio()`: Portfolio performance analysis
  - `assess_portfolio_risk()`: Risk assessment
  - `optimize_portfolio()`: Optimization recommendations
  - `get_user_portfolio_data()`: Access user data through UserDataAgent

#### 5. **Agent Orchestrator** (`orchestrator`)
- **Primary Role**: Intelligent query routing and multi-agent coordination
- **Responsibilities**:
  - Analyze user queries and determine appropriate agents
  - Coordinate single, parallel, and sequential agent execution
  - Synthesize responses from multiple agents
  - Manage context flow between agents
  - Handle error recovery and fallback strategies
 
## 🔄 Agent Graph and Data Flow

### Agent Interaction Graph

```
                    ┌─────────────────┐
                    │   User Query    │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │   Orchestrator  │
                    │   (LLM Router)  │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │  Execution Plan │
                    │  (Single/Parallel/Sequential) │
                    └─────────┬───────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
   ┌────▼────┐          ┌────▼────┐          ┌────▼────┐
   │ Market  │          │Security │          │User Data│
   │ Agent   │          │ Agent   │          │ Agent   │
   └────┬────┘          └────┬────┘          └────┬────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                    ┌─────────▼───────┐
                    │  Portfolio      │
                    │  Agent          │
                    └─────────┬───────┘
                              │
                    ┌─────────▼───────┐
                    │  Response       │
                    │  Synthesis      │
                    └─────────────────┘
```

### Data Flow Patterns

#### 1. **Single Agent Flow**
```
User Query → Orchestrator → Single Agent → Response
```
- **Use Case**: Simple queries like "What's the RSI of AAPL?"
- **Example**: Market news, technical analysis, portfolio summary

#### 2. **Parallel Agent Flow**
```
User Query → Orchestrator → [Agent1, Agent2] → Response Synthesis
```
- **Use Case**: Independent data gathering
- **Example**: "Compare my portfolio to market trends" → UserData + Market agents

#### 3. **Sequential Agent Flow**
```
User Query → Orchestrator → Agent1 → Agent2 → Agent3 → Response Synthesis
```
- **Use Case**: Dependent data processing
- **Example**: "Should I buy more AAPL?" → UserData → Security → Portfolio agents

## 🧠 Decision-Making Processes

### 1. **Query Analysis and Routing**

The orchestrator uses an LLM (GPT-4o-mini) to analyze user queries and determine the execution plan:

```python
# Query Analysis Process
1. Parse user query for intent and context
2. Identify required data sources and analysis types
3. Determine agent dependencies and execution order
4. Generate execution plan (single/parallel/sequential)
5. Create sub-queries for each agent
```

**Decision Factors**:
- Query complexity and scope
- Data dependencies between agents
- User context and portfolio relevance
- Analysis type (technical, fundamental, portfolio)

### 2. **Agent Selection Logic**

```python
# Agent Selection Rules
- "my portfolio", "my holdings" → user_data agent
- "RSI", "moving averages", "MACD" → security agent
- "market news", "sector analysis" → market agent
- "portfolio analysis", "risk assessment" → portfolio agent
- Complex queries → multi-agent coordination
```

### 3. **Execution Plan Generation**

The orchestrator generates execution plans based on query analysis:

```python
# Execution Plan Types
{
    "type": "single|parallel|sequential",
    "agents": ["agent1", "agent2", ...],
    "sub_queries": {
        "agent1": "specific query for agent1",
        "agent2": "specific query for agent2"
    },
    "reasoning": "explanation of plan choice"
}
```

### 4. **Response Synthesis**

For multi-agent queries, the orchestrator synthesizes responses:

```python
# Response Synthesis Process
1. Collect responses from all agents
2. Identify key insights and data points
3. Resolve conflicts and inconsistencies
4. Structure comprehensive response
5. Maintain context and user focus
```

## 🔌 Integration with External Systems

### 1. **Financial Data Sources**

#### **Yahoo Finance (yfinance)**
- **Purpose**: Stock price data, historical data, company information
- **Integration**: Direct API calls for real-time and historical data
- **Usage**: Market Agent, Security Analysis Agent
- **Data Types**: OHLCV data, company profiles, financial metrics

#### **NewsAPI**
- **Purpose**: Financial news and market updates
- **Integration**: REST API with API key authentication
- **Usage**: Market Agent for news aggregation
- **Data Types**: News articles, headlines, market sentiment

#### **Tavily Search**
- **Purpose**: Web search for additional market information
- **Integration**: LangChain Tavily integration
- **Usage**: Market Agent for comprehensive research
- **Data Types**: Web search results, market analysis

### 2. **Database Integration**

#### **PostgreSQL Database**
- **Purpose**: User portfolio data storage and retrieval
- **Integration**: SQLAlchemy ORM with async support
- **Usage**: User Data Agent for portfolio access
- **Data Types**: User holdings, transactions, portfolio history


### 5. **Configuration Management**

#### **Environment Variables**
- **Purpose**: API keys, database connections, system settings
- **Integration**: Pydantic BaseSettings for configuration
- **Usage**: All agents for API access and system configuration
- **Configuration**: OpenAI API key, NewsAPI key, database URL

### 6. **API Endpoints**

#### **FastAPI Integration**
- **Purpose**: REST API for agent system access
- **Integration**: FastAPI with dependency injection
- **Usage**: External system integration, user authentication
- **Endpoints**: Query processing, agent status, system health

#### **API Structure**
```python
# Main API endpoints
POST /api/v1/agents/query - Process user queries
```

## 🔒 Key Features

+ Natural language query support (simple & complex)
+ Multi-agent orchestration for reasoning and collaboration
+ Data security & client isolation
+ Response validation to minimize hallucinations
+ Persistent memory for client profiles and past decisions
+ Error handling & fallback mechanisms

## ⚙️ Tech Stack

+ Framework: LangGraph (or equivalent)
+ Backend: FastAPI
+ Database: PostgreSQL (investment data, user portfolios)
+ Integrations: Financial APIs, news feeds, market data sources
+ Other: Pydantic models, layered architecture for scalability

## 📂 Project Structure
``` bash
investment-advisor-copilot/
│── app/
│   ├── api/                # API routes (FastAPI)
│   ├── models/             # Database models
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── repositories/       # Data access layer
│   ├── utils/              # Helper functions
│── agents/                 # Agent implementations
│── evaluations/            # Agent performance reports
│── requirements.txt        # Dependencies
│── README.md               # Project documentation
```

## 🚀 Getting Started
``` bash
# Clone repo
git clone https://github.com/AnuragKr/investment-advisor-copilot.git
cd investment-advisor-copilot

# Install dependencies
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload
```

Access API docs: http://127.0.0.1:8000/docs


## 🔮 Roadmap

+ Add more specialized agents (e.g., tax advisory, ESG scoring)
+ Improve scalability for multi-client sessions
+ Integrate real-time data feeds for dynamic analysis
+ Expand portfolio simulation and backtesting tools

## 📜 License

Licensed under the MIT License.
