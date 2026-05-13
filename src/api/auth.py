"""Authentication and account lifecycle endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.users import (
    confirm_user_email,
    create_user,
    get_user_by_email,
    update_user_password,
)
from src.database.db import get_db
from src.schemas.base import MessageResponse
from src.schemas.auth import PasswordResetConfirm, PasswordResetRequest, TokenModel
from src.schemas.user import RequestEmail, UserCreate, UserLogin, UserResponse
from src.services.auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from src.services.cache import invalidate_user_cache, set_cached_user
from src.services.email import (
    get_email_from_password_reset_token,
    get_email_from_token,
    send_password_reset_email,
    send_verification_email,
)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user account and trigger email verification."""
    existing_user = await get_user_by_email(db, body.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Account already exists",
        )

    user = await create_user(db, body, get_password_hash(body.password))
    await send_verification_email(user.email, user.username)
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenModel)
async def login_user(
    body: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> TokenModel:
    """Authenticate a verified user and issue an access token."""
    user = await authenticate_user(db, body.email, body.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not verified",
            headers={"WWW-Authenticate": "Bearer"},
        )

    await set_cached_user(user)
    access_token = create_access_token(data={"sub": user.email})
    return TokenModel(access_token=access_token)


@router.get("/verify-email/{token}", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Confirm a user's email address using the verification token."""
    try:
        email = get_email_from_token(token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    user = await get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        return MessageResponse(message="Your email is already verified")

    user = await confirm_user_email(db, user)
    await invalidate_user_cache(user.email)
    await set_cached_user(user)
    return MessageResponse(message="Email verified successfully")


@router.post("/request-email", response_model=MessageResponse)
async def request_email_verification(
    body: RequestEmail,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Resend an email verification message for an existing unverified user."""
    user = await get_user_by_email(db, body.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if user.is_verified:
        return MessageResponse(message="Your email is already verified")

    await send_verification_email(user.email, user.username)
    return MessageResponse(message="Verification email sent")


@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(
    body: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Send a password reset link without exposing whether the email exists."""
    user = await get_user_by_email(db, body.email)
    if user is not None:
        await send_password_reset_email(user.email, user.username)

    return MessageResponse(
        message="If an account with this email exists, a password reset link has been sent",
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    body: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Validate a password reset token and store the new password hash."""
    try:
        email = get_email_from_password_reset_token(body.token)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    user = await get_user_by_email(db, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password reset token",
        )

    await update_user_password(db, user, get_password_hash(body.new_password))
    await invalidate_user_cache(user.email)
    return MessageResponse(message="Password has been reset successfully")
