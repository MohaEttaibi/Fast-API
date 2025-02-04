import logging
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Depends
from database import comment_table, post_table, database
from models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments
from models.user import User
from security import get_current_user, oauth2_scheme

router = APIRouter()

logger = logging.getLogger(__name__)

async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)

@router.post("/post", response_model=UserPost, status_code=201)
# async def create_post(post: UserPostIn,  request: Request):
async def create_post(post: UserPostIn,  current_user: Annotated[User, Depends(get_current_user )]):
    logger.info("Creating post")
    # current_user: User = await get_current_user(await oauth2_scheme(request)) # noqa
    # data = post.dict()
    data = {**post.dict(), "user_id": current_user.id}
    query = post_table.insert().values(data)
    logger.debug(query)
    last_recor_id = await database.execute(query)
    return {**data, "id": last_recor_id}

@router.get("/post", response_model=list[UserPost])
async def get_all_post():
    logger.info("Getting all posts")
    query = post_table.select()
    logger.debug(query)
    return await database.fetch_all(query)

@router.post("/comment", response_model=Comment)
# async def create_comment(comment: CommentIn, request: Request):
async def create_comment(comment: CommentIn, current_user: Annotated[User, Depends(get_current_user )]):
    logger.info("Creating comment")
    # current_user: User = await get_current_user(await oauth2_scheme(request)) # noqa
    post = await find_post(comment.post_id)
    if not post:
        # logger.error(f"Post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    # data = comment.dict()
    data = {**comment.dict(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
    # logger.debug(query, extra={"email": "moha@gmail.com"})
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comment_on_post(post_id: int):
    logger.info(f"Getting all comments on post with {post_id}")
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    logger.debug(query)
    return await database.fetch_all(query)

@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_on_comments(post_id: int):
    logger.info("Getting post and its comments")
    post = await find_post(post_id)
    if not post:
        # logger.error(f"Post with post id {post_id} not found")
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    return {
        "post": post,
        "comments": await get_comment_on_post(post_id)
    }