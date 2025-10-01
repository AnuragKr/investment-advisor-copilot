"""
Portfolio Service Module

This module provides business logic layer operations for portfolio management.
It handles portfolio operations, validation, and all business rules
related to portfolio operations.

The service layer sits between the API controllers and repositories,
implementing business logic, validation, and security measures.

Key Features:
- Portfolio CRUD operations with business rule enforcement
- User-specific portfolio isolation
- Financial data validation and precision
- Comprehensive error handling and logging
- Input validation and sanitization
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.portfolio import PortfolioRepository
from app.schemas.portfolio import PortfolioResponse, PortfolioFilter, PortfolioCreate, PortfolioUpdate
from app.exceptions import PortfolioNotFoundError, DatabaseError, PortfolioAlreadyExistsError, InvalidPortfolioDataError
import logging
from datetime import datetime
from decimal import Decimal

# Configure logging for portfolio service operations
logger = logging.getLogger(__name__)


class PortfolioService:
    """
    Service class for portfolio business logic operations.
    
    This class implements all business logic related to portfolio management,
    including validation, business rule enforcement, and data processing.
    It acts as an intermediary between the API layer and data access layer.
    
    Attributes:
        repo (PortfolioRepository): Repository instance for data access
        session (AsyncSession): Database session for the current operation
        
    Methods:
        create_portfolio: Create new portfolio entry with validation
        update_portfolio: Update existing portfolio entry with business rule checks
        get_portfolio: Retrieve portfolio entry by ID with error handling
        get_portfolios_by_user: Retrieve all portfolio entries for a user
        get_portfolios_by_symbol: Retrieve portfolio entries by symbol for a user
        list_portfolios: Retrieve filtered list of portfolio entries
        delete_portfolio: Delete portfolio entry with validation
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize PortfolioService with database session.
        
        Args:
            session (AsyncSession): Database session for the service operations
        """
        self.repo = PortfolioRepository()
        self.session = session

    def _validate_portfolio_data(self, portfolio_data: dict) -> None:
        """
        Validate portfolio data for business rules.
        
        Args:
            portfolio_data (dict): Portfolio data to validate
            
        Raises:
            InvalidPortfolioDataError: If validation fails
        """
        # Validate quantity is positive
        if portfolio_data.get('quantity', 0) <= 0:
            raise InvalidPortfolioDataError("Quantity must be greater than 0")
        
        # Validate purchase price is positive
        if portfolio_data.get('purchase_price', 0) <= 0:
            raise InvalidPortfolioDataError("Purchase price must be greater than 0")
        
        # Validate sell price if provided
        if portfolio_data.get('sell_price') is not None:
            if portfolio_data['sell_price'] <= 0:
                raise InvalidPortfolioDataError("Sell price must be greater than 0")
        
        # Validate dates
        purchase_date = portfolio_data.get('purchase_date')
        sell_date = portfolio_data.get('sell_date')
        
        if purchase_date and sell_date:
            if sell_date < purchase_date:
                raise InvalidPortfolioDataError("Sell date cannot be before purchase date")

    async def create_portfolio(self, user_id: int, portfolio_in: PortfolioCreate) -> PortfolioResponse:
        """Create a new portfolio entry for the authenticated user."""
        try:
            # Prepare portfolio data and add user_id from authenticated user
            create_data = portfolio_in.model_dump()
            create_data['user_id'] = user_id
            
            # Validate portfolio data
            self._validate_portfolio_data(create_data)
            
            # Set automatic timestamps
            current_time = datetime.now()
            create_data['created_at'] = current_time
            create_data['updated_at'] = current_time
            
            # Create portfolio entry in database
            portfolio_model = await self.repo.create(self.session, create_data)
            logger.info(f"Portfolio entry created successfully with ID: {portfolio_model.portfolio_id} for user {user_id}")
            
            # Return portfolio data
            return PortfolioResponse.model_validate(portfolio_model)
            
        except InvalidPortfolioDataError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to create portfolio entry: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to create portfolio entry")

    async def update_portfolio(self, user_id: int, portfolio_id: int, portfolio_in: PortfolioUpdate) -> PortfolioResponse:
        """Update an existing portfolio entry (only if owned by the authenticated user)."""
        try:
            # Get existing portfolio and verify ownership
            existing_portfolio = await self.repo.get_by_id(self.session, portfolio_id)
            if not existing_portfolio:
                logger.warning(f"Portfolio update failed: portfolio entry {portfolio_id} not found")
                raise PortfolioNotFoundError("Portfolio entry not found")
            
            # Check if the portfolio belongs to the authenticated user
            if existing_portfolio.user_id != user_id:
                logger.warning(f"Portfolio update failed: user {user_id} attempted to update portfolio {portfolio_id} owned by user {existing_portfolio.user_id}")
                raise PortfolioNotFoundError("Portfolio entry not found")
            
            # Prepare update data
            update_data = portfolio_in.model_dump(exclude_unset=True)
            
            # Validate portfolio data if any financial fields are being updated
            if any(field in update_data for field in ['quantity', 'purchase_price', 'sell_price', 'purchase_date', 'sell_date']):
                existing_data = existing_portfolio.model_dump()
                existing_data.update(update_data)
                self._validate_portfolio_data(existing_data)
            
            # Set automatic update timestamp
            update_data['updated_at'] = datetime.now()
            
            # Update portfolio entry in database
            portfolio_model = await self.repo.update(self.session, portfolio_id, update_data)
            logger.info(f"Portfolio entry {portfolio_id} updated successfully by user {user_id}")
            return PortfolioResponse.model_validate(portfolio_model)
            
        except (PortfolioNotFoundError, InvalidPortfolioDataError):
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to update portfolio entry {portfolio_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to update portfolio entry")

    async def get_portfolio(self, user_id: int, portfolio_id: int) -> PortfolioResponse:
        """Retrieve a portfolio entry (only if owned by the authenticated user)."""
        try:
            portfolio_model = await self.repo.get_by_id(self.session, portfolio_id)
            if not portfolio_model:
                logger.warning(f"Portfolio retrieval failed: portfolio entry {portfolio_id} not found")
                raise PortfolioNotFoundError("Portfolio entry not found")
            
            # Check if the portfolio belongs to the authenticated user
            if portfolio_model.user_id != user_id:
                logger.warning(f"Portfolio retrieval failed: user {user_id} attempted to access portfolio {portfolio_id} owned by user {portfolio_model.user_id}")
                raise PortfolioNotFoundError("Portfolio entry not found")
            
            return PortfolioResponse.model_validate(portfolio_model)
            
        except PortfolioNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve portfolio entry {portfolio_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve portfolio entry")

    async def get_portfolios_by_user(self, user_id: int) -> list[PortfolioResponse]:
        """
        Retrieve all portfolio entries for a specific user.
        
        Args:
            user_id (int): ID of the user to retrieve portfolio entries for
            
        Returns:
            list[PortfolioResponse]: List of portfolio data for the user
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            portfolio_model_list = await self.repo.get_by_user_id(self.session, user_id)
            
            if not portfolio_model_list:
                logger.info(f"No portfolio entries found for user {user_id}")
                return []  # Return empty list if no data found
            
            # Convert models to response schemas
            portfolio_responses = [PortfolioResponse.model_validate(portfolio_model) for portfolio_model in portfolio_model_list]
            logger.info(f"Retrieved {len(portfolio_responses)} portfolio entries for user {user_id}")
            
            return portfolio_responses
            
        except Exception as e:
            logger.error(f"Failed to retrieve portfolio entries for user {user_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve portfolio entries")

    async def get_portfolios_by_symbol(self, user_id: int, symbol: str) -> list[PortfolioResponse]:
        """
        Retrieve portfolio entries by symbol for a specific user.
        
        Args:
            user_id (int): ID of the user to filter by
            symbol (str): Symbol to search for
            
        Returns:
            list[PortfolioResponse]: List of portfolio data matching the criteria
            
        Raises:
            DatabaseError: If database operation fails
        """
        try:
            portfolio_model_list = await self.repo.get_by_symbol(self.session, user_id, symbol)
            
            if not portfolio_model_list:
                logger.info(f"No portfolio entries found for user {user_id} with symbol {symbol}")
                return []  # Return empty list if no data found
            
            # Convert models to response schemas
            portfolio_responses = [PortfolioResponse.model_validate(portfolio_model) for portfolio_model in portfolio_model_list]
            logger.info(f"Retrieved {len(portfolio_responses)} portfolio entries for user {user_id} with symbol {symbol}")
            
            return portfolio_responses
            
        except Exception as e:
            logger.error(f"Failed to retrieve portfolio entries for user {user_id} with symbol {symbol}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve portfolio entries")

    async def list_portfolios(self, skip: int = 0, limit: int = 10, filters: PortfolioFilter = None, user_id: int = None) -> list[PortfolioResponse]:
        """
        Retrieve a filtered and paginated list of portfolio entries.
        
        Args:
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            filters (PortfolioFilter, optional): Filter criteria for the query
            user_id (int, optional): Filter by specific user ID
            
        Returns:
            list[PortfolioResponse]: List of portfolio data matching the criteria
            
        Raises:
            DatabaseError: If database operation fails
            
        Note:
            - Empty result sets return an empty list, not None
            - Pagination parameters are validated at the API level
            - Filters support search and asset_class criteria
            - If user_id is provided, results are filtered to that user only
        """
        try:
            portfolio_model_list = await self.repo.get_list(
                self.session, 
                skip=skip, 
                limit=limit, 
                filters=filters,
                user_id=user_id
            )
            
            if not portfolio_model_list:
                logger.info("Portfolio list query returned no results")
                return []  # Return empty list if no data found
            
            # Convert models to response schemas
            portfolio_responses = [PortfolioResponse.model_validate(portfolio_model) for portfolio_model in portfolio_model_list]
            logger.info(f"Retrieved {len(portfolio_responses)} portfolio entries successfully")
            
            return portfolio_responses
            
        except Exception as e:
            logger.error(f"Failed to list portfolio entries: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to list portfolio entries")

    async def delete_portfolio(self, user_id: int, portfolio_id: int) -> bool:
        """Delete a portfolio entry (only if owned by the authenticated user)."""
        try:
            # Get existing portfolio and verify ownership
            existing_portfolio = await self.repo.get_by_id(self.session, portfolio_id)
            if not existing_portfolio:
                logger.warning(f"Portfolio deletion failed: portfolio entry {portfolio_id} not found")
                raise PortfolioNotFoundError("Portfolio entry not found")
            
            # Check if the portfolio belongs to the authenticated user
            if existing_portfolio.user_id != user_id:
                logger.warning(f"Portfolio deletion failed: user {user_id} attempted to delete portfolio {portfolio_id} owned by user {existing_portfolio.user_id}")
                raise PortfolioNotFoundError("Portfolio entry not found")
            
            deleted = await self.repo.delete(self.session, portfolio_id)
            logger.info(f"Portfolio entry {portfolio_id} deleted successfully by user {user_id}")
            return deleted
            
        except PortfolioNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to delete portfolio entry {portfolio_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to delete portfolio entry")
