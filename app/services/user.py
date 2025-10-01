"""User service for business logic and authentication."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user import UserRepository
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.exceptions import UserNotFoundError, DatabaseError, UserAlreadyExistsError
import logging
from datetime import datetime
from passlib.context import CryptContext
from app.utils.security import generate_access_token
logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    """Service for user business logic and authentication."""
    
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository()
        self.session = session

    def _hash_password(self, password: str) -> str:
        """Hash a plain text password using bcrypt."""
        # bcrypt has a 72 byte limit, truncate if necessary
        if len(password.encode('utf-8')) > 72:
            password = password[:72]
        return pwd_context.hash(password)

    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain text password against a hashed password."""
        # bcrypt has a 72 byte limit, truncate if necessary
        if len(plain_password.encode('utf-8')) > 72:
            plain_password = plain_password[:72]
        return pwd_context.verify(plain_password, hashed_password)

    async def create_user(self, user_in: UserCreate) -> UserResponse:
        """Create a new user with validation and security measures."""
        try:
            # Check if user with email already exists to prevent duplicates
            existing_user = await self.repo.get_by_email(self.session, user_in.email_id)
            if existing_user:
                logger.warning(f"User creation failed: email {user_in.email_id} already exists")
                raise UserAlreadyExistsError("User with this email already exists")

            # Prepare user data for creation
            create_data = user_in.model_dump()
            current_time = datetime.now()
            
            # Set automatic timestamps
            create_data['created_at'] = current_time
            create_data['updated_at'] = current_time
            
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
                "name": user_model.name,
                "id": user_model.user_id
            }      })

            return access_token
            
        except UserNotFoundError:
            # Re-raise business logic exceptions
            raise
        except Exception as e:
            logger.error(f"Failed to authenticate user with email {email}: {str(e)}", exc_info=True)
            raise DatabaseError("Failed to authenticate user")