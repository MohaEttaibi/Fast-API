import logging
import sqlalchemy
from enum import Enum
from typing import Annotated
from fastapi import APIRouter, HTTPException, Request, Depends
from database import comment_table, post_table, database, like_table
from models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments, PostLikeIn, PostLike, UserPostWithLikes
from models.user import User
from security import get_current_user, oauth2_scheme

router = APIRouter()

logger = logging.getLogger(__name__)

select_post_and_likes = (
    sqlalchemy.select(post_table,sqlalchemy.func.count(like_table.c.id).label("likes"))
    .select_from(post_table.outerjoin(like_table))
    .group_by(post_table.c.id)
)

async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)

class PostSorting(str, Enum):
    new = "new"
    old = "old"
    most_likes = "most_likes"

@router.get("/post", response_model=list[UserPostWithLikes])
async def get_all_posts(sorting: PostSorting = PostSorting.new):    # http://api.com/post?sorting=most_likes
    logger.info("Getting all posts")
    # match sorting :
    #     case PostSorting.new:
    #         query = select_post_and_likes.order_by(post_table.c.id.desc())
    if sorting == PostSorting.new:
        query = select_post_and_likes.order_by(post_table.c.id.desc())
    if sorting == PostSorting.old:
        query = select_post_and_likes.order_by(post_table.c.id.asc())
    if sorting == PostSorting.most_likes:
        query = select_post_and_likes.order_by(sqlalchemy.desc("likes"))
    logger.debug(query)
    return await database.fetch_all(query)

@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn, current_user: Annotated[User, Depends(get_current_user )]):
    logger.info("Creating post")
    data = {**post.dict(), "user_id": get_current_user.id}
    query = post_table.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

@router.post("/comment", response_model=Comment)
async def create_comment(comment: CommentIn, current_user: Annotated[User, Depends(get_current_user )]):
    logger.info("Creating comment")
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    data = {**comment.dict(), "user_id": current_user.id}
    query = comment_table.insert().values(data)
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
async def get_post_with_comments(post_id: int):
    logger.info("Getting post and its comments")
    query = select_post_and_likes.where(post_table.c.id == post_id)
    logger.debug(query)
    post= await database.fetch_one(query)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    return {
        "post": post,
        "comments": await get_comment_on_post(post_id)
    }

@router.post("/like", response_model=PostLike, status_code=201)
async def like_post(like: PostLikeIn, currnet_user: Annotated[User, Depends(get_current_user)]):
    logger.info("Liking post")
    post = await find_post(like.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    data = {**like.dict(), "user_id": currnet_user.id}
    query = like_post.insert().values(data)
    logger.debug(query)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}