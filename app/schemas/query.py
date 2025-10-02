from pydantic import BaseModel, Field, EmailStr, condecimal
from typing import Optional, List, Dict, Any
from datetime import datetime



class QueryRequest(BaseModel):
    """Request model for agent queries."""
    query: str


class QueryResponse(BaseModel):
    """Response model for agent queries."""
    status: str
    response: str
    agents_used: List[str]
    execution_type: str
    metadata: Dict[str, Any] = {}
