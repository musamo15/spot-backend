from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import router

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers=["*"]
)

app.include_router(router.rout)

@app.get("/")
async def root():
    return {"SPOT RENTAL Platform" : "Welcome to our page!!"}
