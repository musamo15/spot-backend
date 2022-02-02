
from decouple import config

import motor.motor_asyncio
from .models import TestModel, UserModel

client = motor.motor_asyncio.AsyncIOMotorClient(config("DATABASE_URI"))
db = client.SPOT
userCollection = db.User

async def create_user(user : UserModel):
    db_user = UserModel(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        phone_number=user.phone_number,
        address=user.address
    )
    
    await db["Users"].insert_one(db_user)
    
    created_user = await db["Users"].find_one({"_id":db_user.id})
    
    return created_user


async def test(t : TestModel):
    print("Testing")
    # db_user = TestModel(
    #     test=t.test
    # )
  
   
    await testCollection.insert_one({"_id":100,
        "Test":"Hello World"})
    # print("Inserted!!!!!")
    created_test = await testCollection.find_one({"_id":100,
        "Test":"Hello World"})
    print(str(created_test))
    return created_test


    