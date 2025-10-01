"""User repository for database operations."""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from app.models.user import User
from app.models.portfolio import Portfolio


class UserRepository:
    """Repository for user data access operations."""
    
    async def get_by_id(self, db: AsyncSession, user_id: int) -> User:
        """Retrieve a user by ID."""
        result = await db.execute(select(User).where(User.user_id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, db: AsyncSession, email: str) -> User:
        """Retrieve a user by email address."""
        result = await db.execute(select(User).where(User.email_id == email))
        return result.scalar_one_or_none()
    
    async def create(self, db: AsyncSession, create_data: dict) -> User:
        """Create a new user record."""
        # Ensure we don't have an explicit user_id to let the database generate it
        if 'user_id' in create_data:
            del create_data['user_id']
        
        db_obj = User(**create_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(self, db: AsyncSession, user_id: int, update_data: dict) -> User:
        """Update an existing user record."""
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
        """Delete a user and all related portfolio entries."""
        db_obj = await self.get_by_id(db, user_id)
        if not db_obj:
            return False
        
        try:
            # Step 1: Delete all portfolio entries for this user
            await db.execute(
                delete(Portfolio).where(Portfolio.user_id == user_id)
            )
            
            # Step 2: Delete the user record
            await db.delete(db_obj)
            
            # Commit all changes (session is managed by dependency injection)
            await db.commit()
            
            return True
            
        except Exception as e:
            # Rollback on any error
            await db.rollback()
            raise e
