from typing import Union
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import time
from os import listdir
from os.path import isfile, join
import os
import random
import hashlib

app = FastAPI()
 

class Item(BaseModel):
    name: str
    description: Union[str, None] = "Описание товара"
    price: float
    id: Union[int, None] = -1
    
    
class User(BaseModel):
    login:str
    email: str
    password: str
    role: Union[str, None] = "basic role"
    technical_token: Union[str, None] = None
    session_token: Union[str, None] = None
    id: Union[int, None] = -1


class AuthUser(BaseModel):
    login: str
    password: str

def check_signature(request: Request, body: dict = None):
    client_signature = request.headers.get('Authorization')
    current_time = int(time.time())
    body_str = json.dumps(body) if body is not None else "{}"
    
    for time_add in [-3, -2, -1, 0]:
        check_time = str(current_time + time_add)
        
        for file in os.listdir("users"):
            with open(f"users/{file}", 'r') as f:
                user_data = json.load(f)
                user_token = user_data.get('session_token')
                server_signature = hashlib.sha256(f"{user_token}{body_str}{check_time}".encode()).hexdigest()
                if server_signature == client_signature:
                    return
    raise HTTPException(status_code=401, detail="Неверная подпись")

@app.post("/items/create")
def create_item(item: Item, request: Request):
    check_signature(request, item.model_dump())
    
    item.id = int(time.time())
    
    with open(f"items/item_{item.id}.json", 'w') as f:
        json.dump(item.model_dump(), f)
        return item
    
@app.get("/items/print")
def all_items(request: Request):
    check_signature(request)
    
    json_files_names = [file for file in os.listdir('items/') if file.endswith('.json')]
    data = []
    for json_file_name in json_files_names:
        file_path = os.path.join('items/', json_file_name)
        with open(file_path, 'r') as f:
            data.append(json.load(f))
    return data

@app.post("/users/reg")
def create_user(user: User):
       
    # Проверка существования пользователя
    for file in os.listdir("users"):
        with open(f"users/{file}", 'r') as f:
            data = json.load(f)
            if data['login'] == user.login:
                raise HTTPException(status_code=400, detail="Логин уже занят")
            if data['email'] == user.email:
                raise HTTPException(status_code=400, detail="Email уже занят")
            
    user.id = int(time.time())
    user.technical_token = str(random.getrandbits(128))
    user.session_token = hashlib.sha256(f"{user.technical_token}{time.time()}".encode()).hexdigest()
    
    with open(f"users/user_{user.id}.json", 'w') as f:
        json.dump(user.model_dump(), f)
        return user
    
@app.post("/users/auth")
def auth_user(params: AuthUser):
    json_files_names = [file for file in os.listdir('users/') if file.endswith('.json')]
    for json_file_name in json_files_names:
        file_path = os.path.join('users/', json_file_name)
        with open(file_path, 'r') as f:
            json_item = json.load(f)
            user = User(**json_item)
            if user.login == params.login and user.password == params.password:
                
                user.session_token = hashlib.sha256(f"{user.technical_token}{time.time()}".encode()).hexdigest()
                with open(file_path, 'w') as f_write:
                    json.dump(user.model_dump(), f_write)
                return {
                    "login": user.login, 
                    "session_token": user.session_token
                }
            
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")