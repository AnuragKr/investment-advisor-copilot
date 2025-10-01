"""Portfolio repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from app.models.portfolio import Portfolio
from app.schemas.portfolio import PortfolioFilter


class PortfolioRepository:
    """Repository for portfolio data access operations."""
    
    async def get_by_id(self, db: AsyncSession, portfolio_id: int) -> Portfolio:
        """Retrieve a portfolio entry by ID."""
        result = await db.execute(select(Portfolio).where(Portfolio.portfolio_id == portfolio_id))
        return result.scalar_one_or_none()

    async def get_by_user_id(self, db: AsyncSession, user_id: int) -> list[Portfolio]:
        """Retrieve all portfolio entries for a user."""
        result = await db.execute(select(Portfolio).where(Portfolio.user_id == user_id))
        return result.scalars().all()

    async def get_by_symbol(self, db: AsyncSession, user_id: int, symbol: str) -> list[Portfolio]:
        """Retrieve portfolio entries by symbol for a user."""
        result = await db.execute(
            select(Portfolio).where(
                and_(
                    Portfolio.user_id == user_id,
                    Portfolio.symbol == symbol
                )
            )
        )
        return result.scalars().all()

    async def get_list(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10, 
        filters: PortfolioFilter = None,
        user_id: int = None
    ) -> list[Portfolio]:
        """Retrieve a filtered and paginated list of portfolio entries."""
        query = select(Portfolio)
        conditions = []
        
        # Filter by user_id if provided
        if user_id:
            conditions.append(Portfolio.user_id == user_id)
        
        # Apply filters if provided
        if filters:
            
            # Search across symbol and security name fields (case-insensitive)
            if filters.search:
                conditions.append(
                    and_(
                        Portfolio.symbol.ilike(f"%{filters.search}%"),
                        Portfolio.security_name.ilike(f"%{filters.search}%")
                    )
                )
            
            # Filter by asset class (case-insensitive partial match)
            if filters.asset_class:
                conditions.append(Portfolio.asset_class.ilike(f"%{filters.asset_class}%"))
        
        # Apply all conditions if any exist
        if conditions:
            query = query.where(and_(*conditions))
        
        # Execute query with pagination
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, create_data: dict) -> Portfolio:
        """Create a new portfolio record."""
        # Ensure we don't have an explicit portfolio_id to let the database generate it
        if 'portfolio_id' in create_data:
            del create_data['portfolio_id']
        
        db_obj = Portfolio(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, portfolio_id: int, update_data: dict) -> Portfolio:
        """Update an existing portfolio record."""
        db_obj = await self.get_by_id(db, portfolio_id)
        if not db_obj:
            return None
        
        # Update only the fields provided in update_data
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, portfolio_id: int) -> bool:
        """Delete a portfolio record."""
        db_obj = await self.get_by_id(db, portfolio_id)
        if not db_obj:
            return False
        
        try:
            await db.delete(db_obj)
            await db.commit()
            return True
            
        except Exception as e:
            # Rollback on any error
            await db.rollback()
            raise e
