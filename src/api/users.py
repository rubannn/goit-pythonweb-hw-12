from fastapi import APIRouter, Depends, File, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.users import update_avatar_url
from src.database.config import settings
from src.database.db import get_db
from src.models.user import User
from src.schemas.user import UserResponse
from src.services.auth import get_current_user
from src.services.cloudinary_service import upload_avatar
from src.services.rate_limiter import limiter


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
@limiter.limit(settings.RATE_LIMIT_ME)
async def read_users_me(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    _ = request
    return UserResponse.model_validate(current_user)


@router.patch("/avatar", response_model=UserResponse)
async def update_user_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    avatar_url = await upload_avatar(file, current_user.id)
    user = await update_avatar_url(
        db=db,
        user=current_user,
        avatar_url=avatar_url,
    )
    return UserResponse.model_validate(user)
