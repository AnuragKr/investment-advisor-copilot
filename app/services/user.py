"""
User Service Module

This module provides business logic layer operations for user management.
It handles user authentication, authorization, and all business rules
related to user operations.

The service layer sits between the API controllers and repositories,
implementing business logic, validation, and security measures.

Key Features:
- User CRUD operations with business rule enforcement
- Secure password hashing and verification
- User authentication and validation
- Comprehensive error handling and logging
- Input validation and sanitization
"""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserFilter, UserCreate, UserUpdate
from app.exceptions import UserNotFoundError, DatabaseError, UserAlreadyExistsError
import logging
from datetime import datetime
from passlib.context import CryptContext
from app.utils.security import generate_access_token
# Configure logging for user service operations
logger = logging.getLogger(__name__)

# Password hashing context using bcrypt algorithm
# bcrypt is a secure, adaptive hashing algorithm designed for password storage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """
    Service class for user business logic operations.
    
    This class implements all business logic related to user management,
    including authentication, validation, and business rule enforcement.
    It acts as an intermediary between the API layer and data access layer.
    
    Attributes:
        repo (UserRepository): Repository instance for data access
        session (AsyncSession): Database session for the current operation
        
    Methods:
        create_user: Create new user with validation and password hashing
        update_user: Update existing user with business rule checks
        get_user: Retrieve user by ID with error handling
        get_user_by_email: Retrieve user by email for authentication
        list_users: Retrieve filtered list of users
        delete_user: Delete user with validation
        authenticate_user: Verify user credentials for login
    """
    
    def __init__(self):
        """
        Initialize UserService with database session.
        """
        self.repo = UserRepository()

    def _hash_password(self, password: str) -> str:
        """
        Hash a plain text password using bcrypt.
        Args:
            password (str): Plain text password to hash   
        Returns:
            str: Hashed password string

        """
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a plain text password against a hashed password.
        Args:
            plain_password (str): Plain text password to verify
            hashed_password (str): Stored hashed password to compare against
        Returns:
            bool: True if passwords match, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, user_in: UserCreate) -> UserResponse:
        """
        Create a new user with comprehensive validation and security measures.
        Args:
            user_in (UserCreate): User creation data from API request
            
        Returns:
            UserResponse: Created user data (excluding password)
        """
        try:
            # Check if user with email already exists to prevent duplicates
            existing_user = await self.repo.get_by_email(user_in.email)
            if existing_user:
                logger.warning(f"User creation failed: email {user_in.email} already exists")
                raise UserAlreadyExistsError("User with this email already exists")

            # Prepare user data for creation
            create_data = user_in.model_dump()
            
            # Hash password for secure storage
            create_data['password'] = self._hash_password(create_data['password'])
            
            # Create user in database
            user_model = await self.repo.create(self.session, create_data)
            logger.info(f"User created successfully with ID: {user_model.user_id}")
            
            # Return user data without sensitive information
            return UserResponse.model_validate(user_model)
            
        except UserAlreadyExistsError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to create user")

    async def update_user(self, user_id: int, user_in: UserUpdate) -> UserResponse:
        """
        Update an existing user with validation and business rule enforcement.
        
        Args:
            user_id (int): ID of the user to update
            user_in (UserUpdate): User update data from API request
            
        Returns:
            UserResponse: Updated user data (excluding password)
        """
        try:
            # Prepare update data
            update_data = user_in.model_dump(exclude_unset=True)
            
            # Set automatic update timestamp
            update_data['updated_at'] = datetime.now()
            
            # Hash password if it's being updated
            if 'password' in update_data:
                update_data['password'] = self._hash_password(update_data['password'])
                logger.info(f"Password updated for user {user_id}")
            
            # Update user in database
            user_model = await self.repo.update(self.session, user_id, update_data)
            if not user_model:
                logger.warning(f"User update failed: user {user_id} not found")
                raise UserNotFoundError("User not found")
            
            logger.info(f"User {user_id} updated successfully")
            return UserResponse.model_validate(user_model)
            
        except UserNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to update user")

    async def get_user(self, user_id: int) -> UserResponse:
        """
        Retrieve a user by their unique identifier.
        
        Args:
            user_id (int): ID of the user to retrieve
            
        Returns:
            UserResponse: User data (excluding password)
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If database operation fails
            
        Note:
            - Returns user data without sensitive information
            - Comprehensive error logging for debugging
        """
        try:
            user_model = await self.repo.get_by_id(self.session, user_id)
            if not user_model:
                logger.warning(f"User retrieval failed: user {user_id} not found")
                raise UserNotFoundError("User not found")
            
            return UserResponse.model_validate(user_model)
            
        except UserNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve user {user_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve user")

    async def get_user_by_email(self, email: str) -> UserResponse:
        """
        Retrieve a user by their email address.
        
        This method is primarily used for authentication and user lookup
        operations where email is the identifier.
        
        Args:
            email (str): Email address of the user to retrieve
            
        Returns:
            UserResponse: User data (excluding password)
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If database operation fails
            
        Note:
            - Email addresses are unique in the system
            - Useful for login and password reset operations
        """
        try:
            user_model = await self.repo.get_by_email(self.session, email)
            if not user_model:
                logger.warning(f"User retrieval failed: email {email} not found")
                raise UserNotFoundError("User not found")
            
            return UserResponse.model_validate(user_model)
            
        except UserNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to retrieve user with email {email}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to retrieve user")

    async def list_users(self, skip: int = 0, limit: int = 10, filters: UserFilter = None) -> list[UserResponse]:
        """
        Retrieve a filtered and paginated list of users.
        
        Args:
            skip (int): Number of records to skip for pagination
            limit (int): Maximum number of records to return
            filters (UserFilter, optional): Filter criteria for the query
            
        Returns:
            list[UserResponse]: List of user data (excluding passwords)
            
        Raises:
            DatabaseError: If database operation fails
            
        Note:
            - Empty result sets return an empty list, not None
            - Pagination parameters are validated at the API level
            - Filters support  search, city, and country criteria
        """
        try:
            user_model_list = await self.repo.get_list(self.session, skip=skip, limit=limit, filters=filters)
            
            if not user_model_list:
                logger.info("User list query returned no results")
                return []  # Return empty list if no data found
            
            # Convert models to response schemas (excluding sensitive data)
            user_responses = [UserResponse.model_validate(user_model) for user_model in user_model_list]
            logger.info(f"Retrieved {len(user_responses)} users successfully")
            
            return user_responses
            
        except Exception as e:
            logger.error(f"Failed to list users: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to list users")

    async def delete_user(self, user_id: int) -> bool:
        """
        Delete a user from the system.
        
        Args:
            user_id (int): ID of the user to delete
            
        Returns:
            bool: True if deletion was successful
            
        Raises:
            UserNotFoundError: If user doesn't exist
            DatabaseError: If database operation fails
            
        Note:
            - This operation is irreversible
            - Consider implementing soft deletes for production systems
            - May need additional business rule checks (e.g., active orders)
        """
        try:
            deleted = await self.repo.delete(self.session, user_id)
            if not deleted:
                logger.warning(f"User deletion failed: user {user_id} not found")
                raise UserNotFoundError("User not found")
            
            logger.info(f"User {user_id} deleted successfully")
            return deleted
            
        except UserNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to delete user")

    async def authenticate_user(self, email: str, password: str) -> UserResponse:
        """
        Authenticate a user with email and password.
        
        Args:
            email (str): User's email address
            password (str): User's plain text password
            
        Returns:
            UserResponse: Authenticated user data (excluding password)
        """
        try:
            # Retrieve user by email
            user_model = await self.repo.get_by_email(self.session, email)
            if not user_model:
                logger.warning(f"Authentication failed for email {email}: user not found")
                raise UserNotFoundError("Invalid credentials")
            
            # Verify password hash
            if not self._verify_password(password, user_model.password):
                logger.warning(f"Authentication failed for email {email}: invalid password")
                raise UserNotFoundError("Invalid credentials")
            
            logger.info(f"User {user_model.user_id} authenticated successfully")

            access_token = generate_access_token(data={
            "user": {
                "name": user_model.first_name + " " + user_model.last_name,
                "id": user_model.user_id,
                "role": user_model.role,
            }      })

            return access_token
            
        except UserNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to authenticate user with email {email}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to authenticate user")