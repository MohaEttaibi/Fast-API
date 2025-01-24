from fastapi import APIRouter, HTTPException
from database import comment_table, post_table, database
from models.post import UserPost, UserPostIn, Comment, CommentIn, UserPostWithComments

router = APIRouter()

async def find_post(post_id: int):
    query = post_table.select().where(post_table.c.id == post_id)
    return await database.fetch_one(query)

@router.post("/post", response_model=UserPost, status_code=201)
async def create_post(post: UserPostIn):
    data = post.dict()
    query = post_table.insert().values(data)
    last_recor_id = await database.execute(query)
    return {**data, "id": last_recor_id}

@router.get("/post", response_model=list[UserPost])
async def get_all_post():
    query = post_table.select()
    return await database.fetch_all(query)

@router.post("/comment", response_model=Comment)
async def create_comment(comment: CommentIn):
    post = await find_post(comment.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    data = comment.dict()
    query = comment.insert().values(data)
    last_record_id = await database.execute(query)
    return {**data, "id": last_record_id}

@router.get("/post/{post_id}/comments", response_model=list[Comment])
async def get_comment_on_post(post_id: int):
    query = comment_table.select().where(comment_table.c.post_id == post_id)
    return await database.fetch_all(query)

@router.get("/post/{post_id}", response_model=UserPostWithComments)
async def get_post_on_comments(post_id: int):
    post = await find_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post Not Found")
    
    return {
        "post": post,
        "comments": await get_comment_on_post(post_id)
    }