from typing import Union, List
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import time
from os import listdir
from os.path import isfile, join
import os
import random

app = FastAPI() 


class User(BaseModel):
    login:str
    email: str
    password: str
    role: Union[str, None] = "basic role"
    token: Union[str, None] = None
    id: Union[int, None] = -1
 

class AuthUser(BaseModel):
    login: str
    password: str
    

class ArrayRequest(BaseModel):
    array: List[int]


class InsertRequest(BaseModel):
    values: List[int]
    position: str = "end"
    index: int = -1
    
        
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
    user.token = str(random.getrandbits(128))
    
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
                return {"login": user.login, "token": user.token}
            
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

@app.post("/array/")
def post_array(request: ArrayRequest):
    global current_array, sort_array
    current_array = request.array
    sort_array = []
    return {"message": "Массив передан", "array": current_array}

@app.get("/array/")
def get_array():
    if not sort_array:
        raise HTTPException(status_code=404, detail="Массив не был отсортирован")
    return {"message": "Отсортированный массив", "array": sort_array}

@app.get("/array/range/")
def get_array_range(start: int, end: int):
    if not sort_array:
        raise HTTPException(status_code=404, detail="Массив не был отсортирован")
    return {"message": "Часть массива", "array": sort_array[start:end]}

@app.post("/array/generate/")
def generate_array():
    global current_array, sort_array
    random_array = [random.randint(0, 100) for _ in range(10)]
    current_array = random_array
    sort_array = []
    return {"message": "Случайный массив сгенерирован", "array": current_array}

@app.delete("/array/")
def delete_array():
    global current_array, sort_array
    current_array = []
    sort_array = []
    return {"message": "Массив удален"}

@app.post("/sort/")
def sort_array_endpoint():
    global sort_array, current_array
    if not current_array:
        raise HTTPException(status_code=404, detail="Массив не найден")
    sort_array = gnome_sort(current_array.copy())
    return {"message": "Массив отсортирован", "sorted": sort_array}

@app.patch("/array/addelement/")
def add_elements(request: InsertRequest):
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