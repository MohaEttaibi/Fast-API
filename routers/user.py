import logging
from fastapi import APIRouter, HTTPException, status
from database import database, comment_table, post_table, user_table
from models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments
from models.user import UserIn
from security import get_user

router = APIRouter()

logger = logging.getLogger(__name__)

@router.post("/register", status_code=201)
async def register(user: UserIn):
    if await get_user(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already taken."
        )
    query = user_table.insert().values(email=user.email, password=user.password)
    logger.debug(query)
    await database.execute(query)