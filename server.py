from typing import Union, List
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
    

class ArrayRequest(BaseModel):
    array: List[int]


class ArrayRangeRequest(BaseModel):
    start: int
    end: int


class InsertRequest(BaseModel):
    values: List[int]
    index: int = -1
    position: str = "end"
    
    

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


current_array = []
sort_array = []

def gnome_sort(array: List[int]) -> List[int]:
    arr = array.copy()
    n = len(arr)
    i = 0
    while i < n - 1:
        if arr[i] <= arr[i + 1]:
            i += 1
        else:
            arr[i], arr[i + 1] = arr[i + 1], arr[i]
            if i > 0:
                i -= 1
    return arr

@app.post("/array/input/")
def post_array(request: ArrayRequest, request_obj: Request):
    check_signature(request_obj, request.model_dump())
    global current_array, sort_array
    current_array = request.array
    sort_array = []
    return {"message": "Массив передан", "array": current_array}

@app.get("/array/get/")
def get_array(request_obj: Request):
    check_signature(request_obj)
    if not sort_array:
        raise HTTPException(status_code=404, detail="Массив не был отсортирован")
    return {"message": "Отсортированный массив", "array": sort_array}

@app.get("/array/part/")
def get_array_range(request: ArrayRangeRequest, request_obj: Request):
    check_signature(request_obj, request.model_dump())
    if not sort_array:
        raise HTTPException(status_code=404, detail="Массив не был отсортирован")
    return {"message": "Часть массива", "array": sort_array[request.start:request.end]}


@app.post("/array/generate/")
def generate_array(request_obj: Request):
    check_signature(request_obj)
    global current_array, sort_array
    random_array = [random.randint(0, 100) for _ in range(10)]
    current_array = random_array
    sort_array = []
    return {"message": "Случайный массив сгенерирован", "array": current_array}

@app.delete("/array/delete/")
def delete_array(request_obj: Request):
    check_signature(request_obj)
    global current_array, sort_array
    current_array = []
    sort_array = []
    return {"message": "Массив удален"}

@app.post("/array/sort/")
def sort_arr(request_obj: Request):
    check_signature(request_obj)
    global sort_array, current_array
    if not current_array:
        raise HTTPException(status_code=404, detail="Массив не найден")
    sort_array = gnome_sort(current_array.copy())
    return {"message": "Массив отсортирован", "sorted": sort_array}

@app.patch("/array/addelement/")
def add_elements(request: InsertRequest, request_obj: Request):
    print(request)
    check_signature(request_obj, request.model_dump())
    global current_array, sort_array
    if not current_array:
        raise HTTPException(status_code=404, detail="Массив не найден")
    
    if request.position == "start":
        current_array = request.values + current_array
    elif request.position == "end":
        current_array += request.values
    elif request.position == "after":
        if request.index < 0 or request.index >= len(current_array):
            raise HTTPException(status_code=400, detail=f"Индекс за пределами массива")
        current_array[request.index+1:request.index+1] = request.values
    
    sort_array = []
    return {"message": "Элементы добавлены", "array": current_array}