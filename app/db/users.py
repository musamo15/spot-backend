from curses import meta
from fastapi import HTTPException
from http import HTTPStatus

from app.utils.utilities import (get_users_api)
from app.db.models.responseModels import UsersModel
from app.db.models.genericModels import AddressModel
from app.db.listings import (get_user_listings,get_user_rentals)

Users = get_users_api()


async def get_user_data(user_id: str):

    # User returned from mgmnt api request
    try:
        user = Users.get(user_id)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid User Id")
    user_data = dict(**user)
    user_data['listings'] = await __get_user_listings__(user_id)
    user_data['rentals'] = await __get_user_rentals(user_id)
    
    return decode_user(user_data)

async def __get_user_listings__(user_id: str):
    return await get_user_listings(user_id)

async def __get_user_rentals(user_id: str):
    return await get_user_rentals(user_id)


def update_user_data(user_id: str, updated_data: dict):
     # Verify user id 
    try:
        user = Users.get(user_id)
    except Exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Invalid User Id")
    
    if 'user_metadata' in updated_data:
        #Parse valid data
        metadata = updated_data['user_metadata']
        
        validMetaData = dict()
        validMetaData['user_metadata'] = {}
        for key in UsersModel.get_meta_data_keys():
            if key in metadata:
                validMetaData['user_metadata'][key] = metadata[key]
      
        __update_metadata__(user_id,validMetaData)
    
    return get_user_data(user_id)

def __update_metadata__(user_id: str, metadata: dict()):
    """
        metadata = {'user_metadata': {...}}
    """
    # Update the the metadata of the user  
    try:
        Users.update(user_id,metadata)
    except Exception as exception:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST,
                            detail="Unable to update user data" + str(exception))
    
def decode_user(user):
    userDict = dict()
    
    userDict['email'] = user['email']
    
    metaData = user['user_metadata']
    userDict['name'] = metaData['first_name'] + ' ' + metaData['last_name']
    userDict['nickname'] = user['nickname']
    userDict['picture'] = user['picture']

    # Check if address exists
    if len(metaData['address']) > 0:
        userDict['address'] = AddressModel.parse_obj(metaData['address'])
    else:
        userDict['address'] = {
            'street1': '',
            'street2': '',
            'city': '',
            'state': '',
            'zip': '',
            'country': ''
        }

    # Check if phone number exists
    if 'phone' in metaData:
        userDict['phone'] = metaData['phone']
    else:
        userDict['phone'] = ''
    
    # Append listings and rentals associated with the user
    userDict['listings'] = user['listings']
    userDict['rentals'] = user['rentals']
    
    return UsersModel.parse_obj(userDict)
