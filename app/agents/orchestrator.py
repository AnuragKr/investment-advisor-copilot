"""
Agent Orchestrator

Enhanced orchestrator that can handle multiple agent calls for complex queries.
Supports both single and multi-agent execution with intelligent coordination.
"""

import logging
import asyncio
from typing import Dict, Any, List, Union
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from app.config import agents_settings as config

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrator for routing queries to appropriate agents."""
    
    def __init__(self, agent_system):
        self.agent_system = agent_system
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.0,
            api_key=config.OPENAI_API_KEY
        )
        
        # Agent descriptions for routing
        self.agent_descriptions = {
            "market": "Market Analysis Agent - Handles market news, stock information, sector analysis, and financial market data",
            "portfolio": "Portfolio Analysis Agent - Handles portfolio analysis, risk assessment, optimization, and investment recommendations",
            "user_data": "User Data Agent - Handles portfolio data access and analysis",
            "security": "Security Analysis Agent - Handles technical analysis including RSI, Moving Averages, MACD, and other technical indicators"
        }
    
    async def process_query(self, query: str, user_id: str = "default") -> Dict[str, Any]:
        """
        Enhanced query processing: LLM determines execution plan and coordinates multiple agents.
        """
        try:
            logger.info(f"Processing query for user {user_id}: {query[:100]}...")
            
            # Step 1: Determine agent execution plan
            plan = await self._determine_agent_plan(query)
            logger.info(f"Execution plan: {plan['type']} with agents {plan['agents']}")
            
            # Step 2: Execute the plan
            agent_responses = await self._execute_agent_plan(query, plan, user_id)
            
            # Step 3: Synthesize response if multiple agents were used
            if len(agent_responses) > 1:
                synthesized_response = await self._synthesize_multi_agent_response(query, plan, agent_responses)
                execution_type = f"{plan['type']}_multi_agent"
            else:
                synthesized_response = agent_responses[0]["response"]["response"]
                execution_type = plan["type"]
            
            return {
                "status": "success",
                "response": synthesized_response,
                "agents_used": plan["agents"],
                "execution_type": execution_type,
                "metadata": {
                    "user_id": user_id,
                    "plan": plan,
                    "agent_responses": agent_responses
                }
            }
            
        except Exception as e:
            logger.error(f"Error in orchestrator: {e}")
            return {
                "status": "error",
                "response": f"I apologize, but I encountered an error processing your query: {str(e)}",
                "agents_used": [],
                "execution_type": "error",
                "metadata": {"error": str(e)}
            }
    
    async def _select_agent_with_llm(self, query: str) -> str:
        """Use LLM to intelligently select the appropriate agent."""
        
        system_prompt = f"""
        You are an intelligent agent selector. Based on the user query, determine which agent should handle it.

        Available agents:
        - "user_data": {self.agent_descriptions['user_data']}
        - "portfolio": {self.agent_descriptions['portfolio']}
        - "market": {self.agent_descriptions['market']}
        - "security": {self.agent_descriptions['security']}

        Guidelines:
        - For queries about "my portfolio", "my holdings", "what stocks do I own", "do I own [stock]", use "user_data"
        - For portfolio analysis, risk assessment, optimization, recommendations, use "portfolio"
        - For market news, stock prices, sector analysis, market trends, use "market"
        - For technical analysis, RSI, moving averages, MACD, trading signals, use "security"
        - For general investment advice that needs portfolio context, use "portfolio"
        - For specific stock information or market data, use "market"

        Respond with ONLY the agent name: "user_data", "portfolio", "market", or "security"
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User query: {query}")
        ]
        
        response = await self.llm.ainvoke(messages)
        selected_agent = response.content.strip().lower()
        
        # Validate the response
        valid_agents = ["user_data", "portfolio", "market", "security"]
        if selected_agent in valid_agents:
            return selected_agent
        else:
            logger.warning(f"LLM returned invalid agent: {selected_agent}, defaulting to user_data")
            return "user_data"
    
    async def _determine_agent_plan(self, query: str) -> Dict[str, Any]:
        """Use LLM to determine which agents should handle the query and how to coordinate them."""
        
        system_prompt = f"""
        You are an intelligent orchestrator that determines which AI agents should handle a user query.
        
            Available agents:
            - "market": {self.agent_descriptions['market']}
            - "portfolio": {self.agent_descriptions['portfolio']}
            - "user_data": {self.agent_descriptions['user_data']}
            - "security": {self.agent_descriptions['security']}
        
        Analyze the user query and determine:
        1. Which agents are needed (can be one or multiple)
        2. How they should be coordinated (sequential or parallel)
        3. The specific sub-queries for each agent
        
        Respond with a JSON object in this format:
        {{
            "type": "single|parallel|sequential",
            "agents": ["market", "portfolio"],
            "sub_queries": {{
                "market": "specific query for market agent",
                "portfolio": "specific query for portfolio agent"
            }},
            "reasoning": "explanation of why this plan was chosen"
        }}
        
        Guidelines:
        - Use "single" for queries that only need one agent
        - Use "parallel" for queries that need multiple agents working independently (e.g., market news + portfolio analysis)
        - Use "sequential" for queries where one agent's output feeds into another (e.g., get portfolio data first, then analyze it)
        - Use agent names exactly as: "market", "portfolio", or "user_data"
        - Be specific about what each agent should focus on
        
        Agent Selection Rules:
        - For market news, stock info, sector analysis, use "market" agent
        - For portfolio analysis, risk assessment, optimization, use "portfolio" agent
        - For direct portfolio data access (holdings, summary, filters), use "user_data" agent
        - For technical analysis, RSI, moving averages, MACD, trading signals, use "security" agent
        - For queries about "my portfolio", "my holdings", "what stocks do I own", use "user_data" agent
        - For portfolio valuation, analysis, recommendations, use "portfolio" agent
        - For market trends, stock prices, sector performance, use "market" agent
        
        Multi-Agent Examples:
        - "What is my portfolio value?" → single: "user_data"
        - "What stocks do I own?" → single: "user_data"  
        - "Analyze my portfolio risk" → single: "portfolio"
        - "What's the latest news on Apple?" → single: "market"
        - "What's the RSI of AAPL?" → single: "security"
        - "Should I buy more AAPL?" → sequential: ["user_data", "security", "portfolio"] (get portfolio data, analyze AAPL technically, then make recommendation)
        - "How is my portfolio performing vs market trends?" → parallel: ["user_data", "market"] (get portfolio + market data simultaneously)
        - "What's the risk of my current tech holdings given market conditions?" → sequential: ["user_data", "market", "security", "portfolio"] (get portfolio, get market, analyze tech stocks technically, then assess risk)
        - "Compare my tech stocks to market performance" → parallel: ["user_data", "market", "security"] (get portfolio tech holdings + market tech performance + technical analysis)
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"User query: {query}")
        ]
        
        response = await self.llm.ainvoke(messages)
        
        try:
            import json
            plan = json.loads(response.content.strip())
            
            # Validate the plan
            if not isinstance(plan, dict) or "agents" not in plan or "type" not in plan:
                raise ValueError("Invalid plan format")
            
            # Ensure agents are valid
            valid_agents = ["market", "portfolio", "user_data", "security"]
            plan["agents"] = [agent for agent in plan["agents"] if agent in valid_agents]
            
            # Fix agent names if they're using full names
            agent_mapping = {
                "Market Analysis Agent": "market",
                "Portfolio Analysis Agent": "portfolio",
                "User Data Agent": "user_data",
                "Security Analysis Agent": "security",
                "market": "market",
                "portfolio": "portfolio",
                "user_data": "user_data",
                "security": "security"
            }
            plan["agents"] = [agent_mapping.get(agent, agent) for agent in plan["agents"]]
            plan["agents"] = [agent for agent in plan["agents"] if agent in valid_agents]
            
            if not plan["agents"]:
                plan["agents"] = ["market"]  # Default fallback
            
            # Ensure type is valid
            if plan["type"] not in ["single", "parallel", "sequential"]:
                plan["type"] = "single"
            
            # Ensure sub_queries exist
            if "sub_queries" not in plan:
                plan["sub_queries"] = {agent: query for agent in plan["agents"]}
            
            return plan
            
        except Exception as e:
            logger.warning(f"Failed to parse agent plan: {e}, using default single agent")
            return {
                "type": "single",
                "agents": ["market"],
                "sub_queries": {"market": query},
                "reasoning": "Default fallback due to parsing error"
            }
    
    async def _execute_agent_plan(self, query: str, plan: Dict[str, Any], user_id: str = "default") -> List[Dict[str, Any]]:
        """Execute the agent plan by coordinating multiple agents."""
        
        agents = plan["agents"]
        execution_type = plan["type"]
        sub_queries = plan["sub_queries"]
        
        if execution_type == "single":
            # Single agent execution
            agent = agents[0]
            sub_query = sub_queries.get(agent, query)
            response = await self.agent_system.process_query(sub_query, agent, user_id)
            return [{"agent": agent, "query": sub_query, "response": response}]
        
        elif execution_type == "parallel":
            # Parallel execution - all agents work simultaneously
            tasks = []
            for agent in agents:
                sub_query = sub_queries.get(agent, query)
                task = self._execute_single_agent(agent, sub_query, user_id)
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            results = []
            for i, response in enumerate(responses):
                agent = agents[i]
                sub_query = sub_queries.get(agent, query)
                
                if isinstance(response, Exception):
                    results.append({
                        "agent": agent,
                        "query": sub_query,
                        "response": {"status": "error", "response": str(response)},
                        "error": str(response)
                    })
                else:
                    results.append({
                        "agent": agent,
                        "query": sub_query,
                        "response": response
                    })
            
            return results
        
        elif execution_type == "sequential":
            # Sequential execution - agents work one after another with data flow
            results = []
            accumulated_context = ""
            
            for i, agent in enumerate(agents):
                sub_query = sub_queries.get(agent, query)
                
                # Enhance query with context from previous agents
                if accumulated_context:
                    enhanced_query = f"Context from previous analysis:\n{accumulated_context}\n\nCurrent task: {sub_query}"
                else:
                    enhanced_query = sub_query
                
                response = await self._execute_single_agent(agent, enhanced_query, user_id)
                
                results.append({
                    "agent": agent,
                    "query": enhanced_query,
                    "response": response
                })
                
                # Accumulate context for next agent
                if response.get("status") == "success":
                    agent_response = response.get("response", "")
                    accumulated_context += f"Agent {agent} analysis:\n{agent_response}\n\n"
                else:
                    accumulated_context += f"Agent {agent} error: {response.get('response', 'Unknown error')}\n\n"
            
            return results
        
        else:
            # Fallback to single agent
            agent = agents[0] if agents else "market"
            response = await self._execute_single_agent(agent, query, user_id)
            return [{"agent": agent, "query": query, "response": response}]
    
    async def _execute_single_agent(self, agent: str, query: str, user_id: str = "default") -> Dict[str, Any]:
        """Execute a single agent with error handling."""
        try:
            return await self.agent_system.process_query(query, agent, user_id)
        except Exception as e:
            logger.error(f"Error executing agent {agent}: {e}")
            return {
                "status": "error",
                "response": f"Error processing query with {agent} agent: {str(e)}"
            }
    
    async def _synthesize_multi_agent_response(self, query: str, plan: Dict[str, Any], agent_responses: List[Dict[str, Any]]) -> str:
        """Synthesize responses from multiple agents into a cohesive response."""
        
        # Prepare context for synthesis
        agent_context = []
        for result in agent_responses:
            agent = result["agent"]
            response = result["response"]
            agent_context.append(f"Agent: {agent}\nQuery: {result['query']}\nResponse: {response.get('response', 'Error')}")
        
        system_prompt = f"""
        You are a response synthesizer. Your job is to take responses from multiple AI agents
        and create a cohesive, well-structured response that addresses the user's original query.
        
        Guidelines:
        1. Combine insights from all agents into a unified response
        2. Maintain the most relevant and accurate information
        3. Structure the response logically with clear sections
        4. Use bullet points or numbered lists when appropriate
        5. Remove redundancy and conflicting information
        6. Ensure the response directly addresses the user's original query
        7. If there are errors from any agent, acknowledge them but focus on successful responses
        
        Execution type: {plan['type']}
        Original query: {query}
        Plan reasoning: {plan.get('reasoning', 'N/A')}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Agent responses to synthesize:\n\n" + "\n\n".join(agent_context))
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
