"""
User Repository Module

This module provides data access layer operations for user management.
It handles all database interactions related to users including CRUD operations,
search functionality, and data filtering.

The repository pattern separates data access logic from business logic,
making the code more maintainable and testable.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from app.models.user import User
from app.schemas.user import UserFilter


class UserRepository:
    """
    Repository class for user data access operations.
    
    This class encapsulates all database operations related to users,
    providing a clean interface for the service layer to interact with
    the database without exposing SQL details.
    
    Attributes:
        None - Stateless repository pattern
        
    Methods:
        get_by_id: Retrieve user by primary key
        get_by_email: Retrieve user by email address
        get_list: Retrieve filtered list of users with pagination
        create: Create new user record
        update: Update existing user record
        delete: Delete user record
    """

    
    
    async def get_by_id(self, user_id: int) -> User:
        """
        Retrieve a user by their unique identifier.
        Args:
            db (AsyncSession): Database session for the operation
            user_id (int): Primary key of the user to retrieve
        Returns:
            User: User model instance if found, None otherwise
            
        """
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User:
        """
        Retrieve a user by their email address.
        Args:
            db (AsyncSession): Database session for the operation
            email (str): Email address of the user to retrieve  
        Returns:
            User: User model instance if found, None otherwise
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_list(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 10, 
        filters: UserFilter = None
    ) -> list[User]:
        """
        Retrieve a filtered and paginated list of users.
        
        Args:
            db (AsyncSession): Database session for the operation
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            filters (UserFilter, optional): Filter criteria for the query
            
        Returns:
            list[User]: List of user model instances matching the criteria
            
        Note:
            - Pagination is handled through skip/limit parameters
            - Filters are applied using AND logic (all conditions must match)
            - Search filter performs case-insensitive matching across multiple fields
            - Empty result sets return an empty list, not None
        """
        query = select(User)
        conditions = []
        
        # Apply filters if provided
        if filters:
            
            # Search across multiple user fields (case-insensitive)
            if filters.search:
                conditions.append(
                    and_(
                        User.first_name.ilike(f"%{filters.search}%"),
                        User.last_name.ilike(f"%{filters.search}%"),
                        User.email.ilike(f"%{filters.search}%")
                    )
                )
            
            # Filter by city (case-insensitive partial match)
            if filters.city:
                conditions.append(User.city.ilike(f"%{filters.city}%"))
            
            # Filter by country (exact match)
            if filters.country:
                conditions.append(User.country == filters.country)
        
        # Apply all conditions if any exist
        if conditions:
            query = query.where(and_(*conditions))
        
        # Execute query with pagination
        result = await db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()
    
    async def create(self, db: AsyncSession, create_data: dict) -> User:
        """
        Create a new user record in the database.
        
        Args:
            db (AsyncSession): Database session for the operation
            create_data (dict): Dictionary containing user data for creation
            
        Returns:
            User: Created user model instance with generated ID
            
        Note:
            - The user object is automatically added to the session
            - Changes are committed to the database
            - The object is refreshed to include generated values (e.g., ID)
            - Explicitly handles ID generation to avoid conflicts
        """
        # Ensure we don't have an explicit user_id to let the database generate it
        if 'user_id' in create_data:
            del create_data['user_id']
        
        db_obj = User(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, user_id: int, update_data: dict) -> User:
        """
        Update an existing user record in the database.
        
        Args:
            db (AsyncSession): Database session for the operation
            user_id (int): Primary key of the user to update
            update_data (dict): Dictionary containing fields to update
            
        Returns:
            User: Updated user model instance, None if user not found
            
        Note:
            - Only provided fields are updated (partial updates supported)
            - The object is refreshed after update to reflect changes
            - Returns None if the user doesn't exist
        """
        db_obj = await self.get_by_id(db, user_id)
        if not db_obj:
            return None
        
        # Update only the fields provided in update_data
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, user_id: int) -> bool:
        """
        Delete a user record from the database along with all related data.
        
        This method performs a cascading delete operation that removes:
        1. All order items associated with the user's orders
        2. All orders associated with the user
        3. The user record itself
        
        Args:
            db (AsyncSession): Database session for the operation
            user_id (int): Primary key of the user to delete
            
        Returns:
            bool: True if deletion was successful, False if user not found
            
        Note:
            - This operation is irreversible and removes all user-related data
            - Returns False if the user doesn't exist
            - Uses the existing session transaction managed by dependency injection
        """
        db_obj = await self.get_by_id(db, user_id)
        if not db_obj:
            return False
        
        try:
            await db.delete(db_obj)
            
            # Commit all changes (session is managed by dependency injection)
            await db.commit()
            
            return True
            
        except Exception as e:
            # Rollback on any error
            await db.rollback()
            raise e
