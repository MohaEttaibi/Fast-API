import logging
from fastapi import APIRouter, HTTPException, status
from database import database, comment_table, post_table, user_table
from models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments
from models.user import UserIn
from security import get_user, get_password_hash, authenticate_user, create_access_token

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already taken."
        )

    hashed_password = get_password_hash(user.password)
    query = user_table.insert().values(email=user.email, password=hashed_password)
    logger.debug(query)
    await database.execute(query)
    return {"detail": "User creadted."}


@router.post("/token")
async def login(user: UserIn):
    user = await authenticate_user(user.email, user.password)
    access_token = create_access_token(user.email)
    return {"access_token": access_token, "token_type": "bearer"}