"""Portfolio API endpoints for management operations."""

from fastapi import APIRouter, HTTPException, Depends
from app.core.dependencies import PortfolioServiceDep, CurrentUserDep
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioResponse, PortfolioFilter
from app.exceptions import PortfolioNotFoundError, DatabaseError, InvalidPortfolioDataError
from app.models.user import User
from typing import Optional

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


@router.get("/{portfolio_id}", response_model=PortfolioResponse)
async def get_portfolio(service: PortfolioServiceDep, current_user: CurrentUserDep, portfolio_id: int):
    """Retrieve a portfolio entry by ID (only if owned by authenticated user)."""
    try:
        db_portfolio = await service.get_portfolio(current_user.user_id, portfolio_id)
        return db_portfolio
    except PortfolioNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio entry not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve portfolio entry at this time")


@router.get("/", response_model=list[PortfolioResponse])
async def list_portfolios(
    service: PortfolioServiceDep,
    current_user: CurrentUserDep,
    skip: int = 0, 
    limit: int = 10,
    search: Optional[str] = None,
    asset_class: Optional[str] = None
):
    """Retrieve authenticated user's portfolio entries with filtering."""
    try:
        filters = PortfolioFilter(search=search, asset_class=asset_class)
        return await service.list_portfolios(skip=skip, limit=limit, filters=filters, user_id=current_user.user_id)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve portfolio entries at this time")


@router.post("/", response_model=PortfolioResponse)
async def create_portfolio(service: PortfolioServiceDep, current_user: CurrentUserDep, portfolio: PortfolioCreate):
    """Create a new portfolio entry for authenticated user."""
    try:
        return await service.create_portfolio(current_user.user_id, portfolio)
    except InvalidPortfolioDataError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to create portfolio entry at this time")


@router.put("/{portfolio_id}", response_model=PortfolioResponse)
async def update_portfolio(service: PortfolioServiceDep, current_user: CurrentUserDep, portfolio_id: int, portfolio: PortfolioUpdate):
    """Update an existing portfolio entry (only if owned by authenticated user)."""
    try:
        return await service.update_portfolio(current_user.user_id, portfolio_id, portfolio)
    except PortfolioNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio entry not found")
    except InvalidPortfolioDataError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to update portfolio entry at this time")


@router.delete("/{portfolio_id}")
async def delete_portfolio(service: PortfolioServiceDep, current_user: CurrentUserDep, portfolio_id: int):
    """Delete a portfolio entry (only if owned by authenticated user)."""
    try:
        await service.delete_portfolio(current_user.user_id, portfolio_id)
        return {"message": "Portfolio entry deleted successfully"}
    except PortfolioNotFoundError:
        raise HTTPException(status_code=404, detail="Portfolio entry not found")
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to delete portfolio entry at this time")


@router.get("/my-portfolios", response_model=list[PortfolioResponse])
async def get_my_portfolios(service: PortfolioServiceDep, current_user: CurrentUserDep):
    """Retrieve all portfolio entries for authenticated user."""
    try:
        return await service.get_portfolios_by_user(current_user.user_id)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve portfolio entries at this time")


@router.get("/my-portfolios/symbol/{symbol}", response_model=list[PortfolioResponse])
async def get_my_portfolios_by_symbol(service: PortfolioServiceDep, current_user: CurrentUserDep, symbol: str):
    """Retrieve authenticated user's portfolio entries by symbol."""
    try:
        return await service.get_portfolios_by_symbol(current_user.user_id, symbol)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve portfolio entries at this time")