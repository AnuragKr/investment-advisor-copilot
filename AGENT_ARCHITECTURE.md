# Production-Grade Agent System

A scalable, production-ready AI agent system for investment advisory services with inter-agent communication capabilities.

## 🏗️ Architecture Overview

The system is built with a modular, production-grade architecture that supports:

- **Scalable Agent Creation**: Easy creation of new specialized agents
- **Inter-Agent Communication**: Agents can communicate and collaborate
- **Configuration Management**: Centralized configuration with environment-specific settings
- **Error Handling**: Comprehensive error handling and logging
- **Monitoring**: Built-in status monitoring and health checks
- **Extensibility**: Plugin-based architecture for easy extension

## 📁 Project Structure

```
app/agents/
├── base.py                    # Core agent architecture and base classes
├── config.py                  # Configuration management system
├── main.py                    # Main agent system orchestrator
├── market_analysis_agent.py   # Market analysis specialized agent
├── portfolio_analysis_agent.py # Portfolio analysis specialized agent
├── react.py                   # Legacy tools (for backward compatibility)
├── nodes.py                   # Legacy nodes (for backward compatibility)
└── market_agent.py           # Legacy market agent (for backward compatibility)

app/config/
└── agents.yaml               # Agent configuration file

demo_agents.py                # Comprehensive demo script
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create a `.env` file with your API keys:

```bash
OPENAI_API_KEY=your_openai_api_key
NEWS_API_KEY=your_news_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### 3. Run the Demo

```bash
python demo_agents.py
```

### 4. Use Individual Agents

```python
from app.agents.main import AgentSystem
from app.agents.config import Environment

# Initialize the agent system
agent_system = AgentSystem(environment=Environment.DEVELOPMENT)
await agent_system.initialize_agents()

# Process a query
result = await agent_system.process_query(
    "What is the latest news on Microsoft?", 
    "market_analysis"
)
print(result['response'])
```

## 🤖 Available Agents

### Market Analysis Agent
- **Capabilities**: Market news, sector analysis, SEC filings, web search
- **Tools**: News API, Yahoo Finance, SEC EDGAR API, Tavily Search
- **Use Case**: Market research and financial news analysis

### Portfolio Analysis Agent
- **Capabilities**: Portfolio analysis, risk assessment, optimization, reporting
- **Tools**: Performance metrics, risk calculations, optimization algorithms
- **Use Case**: Portfolio management and risk analysis

## 🔧 Creating New Agents

### 1. Define Agent Class

```python
from app.agents.base import BaseAgent, AgentConfig

class MyCustomAgent(BaseAgent):
    def __init__(self, config: AgentConfig, registry=None):
        super().__init__(config, registry)
    
    def _initialize_tools(self) -> List:
        # Define your tools here
        return [my_custom_tool]
    
    def _get_system_message(self) -> str:
        # Define your system message
        return "You are a specialized agent for..."
```

### 2. Register Agent

```python
from app.agents.base import AgentFactory
AgentFactory.register_agent_class("my_custom", MyCustomAgent)
```

### 3. Add Configuration

Add your agent configuration to `app/config/agents.yaml`:

```yaml
agents:
  my_custom:
    name: "My Custom Agent"
    description: "Description of what this agent does"
    capabilities:
      - "capability1"
      - "capability2"
    tools:
      - "tool1"
      - "tool2"
```

## 🔄 Inter-Agent Communication

Agents can communicate with each other using the message system:

```python
# Send a message to another agent
await agent.send_message_to_agent(
    recipient_id="other_agent_id",
    content="Please analyze this data",
    message_type=MessageType.REQUEST
)

# Broadcast to all agents
await agent.broadcast_to_all("Market update: Tech sector up 5%")

# Handle incoming messages
async def _handle_request(self, message: AgentMessage) -> None:
    # Process the request
    response = await self.process_query(message.content)
    
    # Send response back
    await self.send_message_to_agent(
        message.sender_id,
        response["response"],
        MessageType.RESPONSE,
        correlation_id=message.id
    )
```

## ⚙️ Configuration Management

The system uses a centralized configuration management system:

```python
from app.agents.config import ConfigManager, Environment

# Initialize config manager
config_manager = ConfigManager(environment=Environment.PRODUCTION)

# Get agent configuration
agent_config = config_manager.get_agent_config("market_analysis")

# Get API configuration
api_config = config_manager.get_api_config()
```

### Configuration Files

- `app/config/agents.yaml`: Agent configurations
- `app/config/config_development.yaml`: Development-specific settings
- `app/config/config_production.yaml`: Production-specific settings

## 📊 Monitoring and Status

Monitor agent status and health:

```python
# Get status of all agents
status = agent_system.get_agent_status()

for agent_name, agent_status in status.items():
    print(f"Agent: {agent_name}")
    print(f"Status: {agent_status['status']}")
    print(f"Capabilities: {agent_status['capabilities']}")
```

## 🔒 Security Features

- **API Key Management**: Secure handling of API keys through environment variables
- **Input Validation**: Pydantic models for configuration validation
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Built-in rate limiting capabilities

## 🧪 Testing

Run the comprehensive demo to test all features:

```bash
python demo_agents.py
```

The demo includes:
- Market analysis capabilities
- Portfolio analysis capabilities
- Inter-agent communication
- Status monitoring
- Scalability testing

## 📈 Performance Features

- **Async Processing**: Full async/await support for high performance
- **Concurrent Execution**: Multiple agents can process queries simultaneously
- **Resource Management**: Efficient resource usage and cleanup
- **Caching**: Built-in caching mechanisms for improved performance

## 🔧 Development

### Adding New Tools

1. Create a tool function with the `@tool` decorator
2. Add it to your agent's `_initialize_tools()` method
3. Update the agent's capabilities in the configuration

### Adding New Capabilities

1. Define the capability in your agent class
2. Update the configuration file
3. Implement the capability logic in your agent

## 📝 Logging

The system includes comprehensive logging:

```python
import logging

# Configure logging level
logging.basicConfig(level=logging.INFO)

# Logs include:
# - Agent initialization
# - Query processing
# - Inter-agent communication
# - Error handling
# - Performance metrics
```

## 🚀 Production Deployment

For production deployment:

1. Set environment to `Environment.PRODUCTION`
2. Configure production-specific settings
3. Set up proper logging and monitoring
4. Configure API keys and secrets
5. Set up health checks and alerting

## 🤝 Contributing

1. Follow the established architecture patterns
2. Add comprehensive error handling
3. Include logging for debugging
4. Update configuration files as needed
5. Add tests for new functionality

## 📄 License

This project is part of the Investment Advisor Copilot system.

---

For more information, see the individual agent documentation and configuration files.
