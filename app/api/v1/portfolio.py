"""Portfolio API endpoints for management operations."""

from fastapi import APIRouter, HTTPException, Depends, Body
from app.core.dependencies import PortfolioServiceDep, CurrentUserDep
from app.schemas.portfolio import PortfolioCreate, PortfolioUpdate, PortfolioResponse, PortfolioFilter
from app.exceptions import PortfolioNotFoundError, DatabaseError, InvalidPortfolioDataError
from app.models.user import User
from typing import Optional, Union

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


@router.post("/", response_model=Union[PortfolioResponse, list[PortfolioResponse]], status_code=201)
async def create_portfolio(
    service: PortfolioServiceDep, 
    current_user: CurrentUserDep, 
    portfolio: Union[PortfolioCreate, list[PortfolioCreate]] = Body(...)
):
    """Create portfolio entry/entries for authenticated user. Accepts single object or array."""
    try:
        # Check if input is a list (bulk creation)
        if isinstance(portfolio, list):
            created_portfolios = []
            for idx, item in enumerate(portfolio):
                try:
                    created_portfolio = await service.create_portfolio(current_user.user_id, item)
                    created_portfolios.append(created_portfolio)
                except Exception as e:
                    raise HTTPException(
                        status_code=422, 
                        detail=f"Error creating portfolio at index {idx}: {str(e)}"
                    )
            return created_portfolios
        else:
            # Single portfolio creation
            return await service.create_portfolio(current_user.user_id, portfolio)
    except InvalidPortfolioDataError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


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


@router.get("/symbol/{symbol}", response_model=list[PortfolioResponse])
async def get_my_portfolios_by_symbol(service: PortfolioServiceDep, current_user: CurrentUserDep, symbol: str):
    """Retrieve authenticated user's portfolio entries by symbol."""
    try:
        return await service.get_portfolios_by_symbol(current_user.user_id, symbol)
    except DatabaseError:
        raise HTTPException(status_code=500, detail="Unable to retrieve portfolio entries at this time")