"""
Agent API Endpoints

Simple API for interacting with AI agents through natural language queries.
"""

from fastapi import APIRouter, HTTPException
import logging

from app.agents.main import AgentSystem
from app.agents.orchestrator import AgentOrchestrator
from app.schemas.query import QueryRequest, QueryResponse
from app.core.dependencies import CurrentUserDep, PortfolioServiceDep

logger = logging.getLogger(__name__)

router = APIRouter()

# Note: Agent system and orchestrator are now created per request with user context


router = APIRouter(prefix="/agents", tags=["agents"])

@router.post("/query", response_model=QueryResponse)
async def query_agent(
    request: QueryRequest, 
    user: CurrentUserDep,
    portfolio_service: PortfolioServiceDep
):
    """
    Send a natural language query to the agent system.
    
    The orchestrator will automatically determine which agent to use
    and synthesize the response.
    """
    try:
        logger.info(f"Received query: {request.query[:100]}...")
        
        # Create agent system with user-specific services
        agent_system = AgentSystem(
            portfolio_service=portfolio_service,
            current_user=user
        )
        
        # Create orchestrator with the user-specific agent system
        orchestrator = AgentOrchestrator(agent_system)
        
        # Use orchestrator to process the query
        result = await orchestrator.process_query(request.query, user.user_id)
        
        return QueryResponse(
            status=result["status"],
            response=result["response"],
            agents_used=result["agents_used"],
            execution_type=result["execution_type"],
            metadata=result.get("metadata", {})
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_agents(user: CurrentUserDep):
    """List all available agents."""
    try:
        # Create a basic agent system for listing
        agent_system = AgentSystem()
        agents = agent_system.list_agents()
        return {
            "status": "success",
            "agents": agents
        }
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check(user: CurrentUserDep):
    """Health check endpoint."""
    try:
        # Create a basic agent system for health check
        agent_system = AgentSystem()
        return {
            "status": "healthy",
            "service": "agent-api",
            "agents_available": len(agent_system.agents)
        }
    except Exception as e:
        logger.error(f"Error in health check: {e}")
        return {
            "status": "unhealthy",
            "service": "agent-api",
            "error": str(e)
        }
