import logging
from fastapi import APIRouter, HTTPException
from database import comment_table, post_table, database
from models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments

router = APIRouter()

logger = logging.getLogger(__name__)

async def find_post(post_id: int):
    logger.info(f"Finding post with id {post_id}")
    query = post_table.select().where(post_table.c.id == post_id)
    logger.debug(query)
    return await database.fetch_one(query)

@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    logger.info("Creating post")
    data = post.dict()
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
async def create_comment(comment: CommentIn):
    logger.info("Creating comment")
    post = await find_post(comment.post_id)
    if not post:
        # logger.error(f"Post with id {comment.post_id} not found")
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    data = comment.dict()
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