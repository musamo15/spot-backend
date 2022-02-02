from fastapi import APIRouter,Request
from app.db.models import UserModel,TestModel
from app.db.crud import (create_user,test)



rout = APIRouter()

@rout.get("/test")
async def root():
    return {"SPOT RENTAL Platform" : "Welcome to our page!!"}

@rout.post("/users",response_model=UserModel,response_model_exclude_none=True)
async def user_create(request:Request,user:UserModel):
    return create_user(user)

@rout.post("/test")
async def user_test(user:TestModel):
    await test(user)
    return "done"
