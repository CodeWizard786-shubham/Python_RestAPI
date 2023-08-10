from fastapi import FastAPI, Request, Depends, HTTPException, status, Response
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()  # fastapi instance
security = HTTPBasic()  # security instance
authenticated_users = set()  # Set data structure to keep track of authenticated users

def authenticate_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = os.getenv('USERNAME')
    correct_password = os.getenv('PASSWORD')

    if credentials.username == correct_username and credentials.password == correct_password:
        authenticated_users.add(credentials.username)  # Adding authenticated user to the set
        return credentials.username

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Basic"},
    )

db = {}

class Item(BaseModel):
    name: str
    age: int

@app.post('/insert/', dependencies=[Depends(authenticate_user)])
async def post_data(item: Item,name:str,age:int, username: str = Depends(authenticate_user)):
    if username not in authenticated_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )
    item.name =name
    item.age=age
    db[item.name] = item.age
    return {'items': item}

# Retrive Particular db record
@app.get('/get/', dependencies=[Depends(authenticate_user)])
async def get_data(name: str, request: Request, username: str = Depends(authenticate_user)):
    if username not in authenticated_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )

    name = request.query_params.get('name')
    age = db.get(name)
    if age is None:
        return Response(content='<error>Item not found</error>', media_type='text/xml')
    else:
        xml_str = f'<data><name>{name}</name><age>{age}</age></data>'
        return Response(content=xml_str, media_type='text/xml')


# retrive entire db records
@app.get("/", dependencies=[Depends(authenticate_user)])
def get_full_data(username: str = Depends(authenticate_user)):
    if username not in authenticated_users:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not authenticated",
            headers={"WWW-Authenticate": "Basic"},
        )

    xml_str = '<data>'
    for key, value in db.items():
        xml_str += f'<name>{key}</name>'
        xml_str += f'<age>{value}</age>'
    xml_str += '</data>'
    
    return Response(content=xml_str, media_type='text/xml')
