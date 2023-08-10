from pydantic import BaseModel
from fastapi import FastAPI ,Path,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError, jwt
import json
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
app = FastAPI()
class User():
    def __init__(self, username: str, password_hash: str):
        self.username = username
        self.password_hash = password_hash


users = {
    "admin": User("admin", pwd_context.hash("password")),
}
oauth_schema = OAuth2PasswordBearer(tokenUrl="token")

def authenticate_user(username, password):
    user = json.loads(User.objects.get(username = username).to_json())

    if user:
        password_check = pwd_context.verify(password,user['password'])
        return password_check
    else:
        return False
    

@app.post("/token")
async def login(form_data:OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if authenticate_user(username,password):
        return {"access_token": username, "token_type":"bearer"}
    else:
        raise HTTPException(status_code=400 , detail="Incorrect username or password")

@app.get("/login")
def home(token: str= Depends(oauth_schema)):
    return { 'token' : token}


db={}
class Item(BaseModel):
    name:str
    age: int

students = {
    1:{
        "name":"john",
        "age" : 17,
        "Class" : "year 12"
    }
}

# @app.get("/")
# def read_root():
#     return {"Hello":"World"}

@app.get("/get-student/{student_id}")
def get_student(student_id: int = Path(description="The ID of the student you want to view",gt=0)):
    return students[student_id]

@app.post("/")
def create(item:Item,name:str,age:int):
    item.name = name
    item.age = age
    db[item.name] = item.age
    return {'items':item}


@app.get("/")
def get_data():
    return db

@app.put("/")
def put_data(item:Item,name:str,age:int):
    item.name = name
    item.age = age
    db[item.name] = item.age
    return {db}


@app.delete("/")
def delete_data(name:str):
    del db[name]
    return db