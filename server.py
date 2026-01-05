from typing import Union, List
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import json
import time
import os
import random
import hashlib

app = FastAPI()


class User(BaseModel):
    login: str
    email: str
    password: str
    technical_token: Union[str, None] = None
    session_token: Union[str, None] = None
    id: Union[int, None] = -1
    current_array: List[int] = []
    sorted_array: List[int] = []


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


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


def get_user_by_token(request: Request, body: dict = None) -> User:
    client_signature = request.headers.get('Authorization')
    if not client_signature:
        raise HTTPException(status_code=401, detail="Отсутствует подпись")
    
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
                    return User(**user_data)
    raise HTTPException(status_code=401, detail="Неверная подпись")


def save_user(user: User):
    with open(f"users/user_{user.id}.json", 'w') as f:
        json.dump(user.model_dump(), f)


def save_history(user_id: int, operation_type: str, details: str):
    history_file = f"history/history_{user_id}.json"
    if not os.path.exists(history_file):
        return
    
    with open(history_file, 'r') as f:
        history = json.load(f)
    
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    history_add = {
        "user": user_id,
        "time": current_time,
        "operation": operation_type,
        "details": details
    }
    history.append(history_add)
    
    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)


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


@app.post("/users/reg")
def create_user(user: User):
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
    
    save_user(user)
    
    with open(f"history/history_{user.id}.json", 'w') as f:
        json.dump([], f)
    
    save_history(user.id, "register", "Пользователь зарегистрирован")
    return {
        "message": "Успешная регистрация",
        "login": user.login,
        "session_token": user.session_token
    }


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
                save_user(user)
                save_history(user.id, "auth", "Успешная авторизация")
                return {
                    "message": "Успешная авторизация",
                    "login": user.login,
                    "session_token": user.session_token
                }
    
    raise HTTPException(status_code=401, detail="Неверный логин или пароль")


@app.post("/array/input")
def post_array(request: ArrayRequest, request_obj: Request):
    user = get_user_by_token(request_obj, request.model_dump())
    
    user.current_array = request.array
    user.sorted_array = []
    save_user(user)
    
    save_history(user.id, "input_array", f"Введен массив")
    return {"message": "Массив передан", "array": user.current_array}


@app.post("/array/generate")
def generate_array(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    random_array = [random.randint(0, 100) for _ in range(10)]
    user.current_array = random_array
    user.sorted_array = []
    save_user(user)
    
    save_history(user.id, "generate_array", f"Сгенерирован массив")
    return {"message": "Случайный массив сгенерирован", "array": user.current_array}


@app.get("/array/get")
def get_array(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    if not user.sorted_array:
        raise HTTPException(status_code=404, detail="Массив не был отсортирован")
    
    save_history(user.id, "array_get", f"Получен массив")
    return {"message": "Отсортированный массив", "array": user.sorted_array}


@app.get("/array/part")
def get_array_range(request: ArrayRangeRequest, request_obj: Request):
    user = get_user_by_token(request_obj, request.model_dump())
    
    if not user.sorted_array:
        raise HTTPException(status_code=404, detail="Массив не был отсортирован")
    
    if request.start < 0 or request.end > len(user.sorted_array) or request.start >= request.end:
        raise HTTPException(status_code=400, detail="Некорректный диапазон")
    
    save_history(user.id, "array_get", f"Получена часть массива")
    return {"message": "Часть массива", "array": user.sorted_array[request.start:request.end]}


@app.post("/array/sort")
def sort_arr(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    if not user.current_array:
        raise HTTPException(status_code=404, detail="Массив не найден")
    
    user.sorted_array = gnome_sort(user.current_array.copy())
    save_user(user)
    
    save_history(user.id, "sort_array", f"Отсортирован массив")
    return {"message": "Массив отсортирован", "array": user.sorted_array}


@app.delete("/array/delete")
def delete_array(request_obj: Request):
    user = get_user_by_token(request_obj)
    user.current_array = []
    user.sorted_array = []
    save_user(user)
    save_history(user.id, "delete_array", "Массив удален")
    return {"message": "Массив удален", "array": user.current_array}


@app.patch("/array/addelement")
def add_elements(request: InsertRequest, request_obj: Request):
    user = get_user_by_token(request_obj, request.model_dump())
    
    if not user.current_array:
        raise HTTPException(status_code=404, detail="Массив не найден")
    
    if request.position == "start":
        user.current_array = request.values + user.current_array
    elif request.position == "end":
        user.current_array += request.values
    elif request.position == "after":
        if request.index < 0 or request.index >= len(user.current_array):
            raise HTTPException(status_code=400, detail=f"Индекс за пределами массива")
        user.current_array[request.index+1:request.index+1] = request.values
    
    user.sorted_array = []
    save_user(user)
    
    save_history(user.id, "add_elements", f"Добавлены элементы")
    return {"message": "Элементы добавлены", "array": user.current_array}


@app.get("/users/history")
def get_user_history(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    history_file = f"history/history_{user.id}.json"
    
    with open(history_file, 'r') as f:
        history = json.load(f)
        
    if history == []:
        return {"message": "История пуста", "history": history}
    
    return {
        "message": "История запросов",
        "history": history
    }


@app.delete("/users/history")
def delete_user_history(request_obj: Request):
    user = get_user_by_token(request_obj)
    
    history_file = f"history/history_{user.id}.json"
    if os.path.exists(history_file):
        
        with open(history_file, 'w') as f:
            json.dump([], f)
            
    return {"message": "История удалена"}


@app.patch("/users/password")
def change_password(request: PasswordChange, request_obj: Request):
    user = get_user_by_token(request_obj, request.model_dump())
    
    user_file = f"users/user_{user.id}.json"
    if not os.path.exists(user_file):
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    with open(user_file, 'r') as f:
        user_data = json.load(f)
    if user_data['password'] != request.old_password:
        raise HTTPException(status_code=400, detail="Неверный старый пароль")
    
    user_data['password'] = request.new_password
    user_data['technical_token'] = hashlib.sha256(f"{time.time()}{random.getrandbits(256)}".encode()).hexdigest()
    user_data['session_token'] = hashlib.sha256(f"{user_data['technical_token']}{time.time()}".encode()).hexdigest()
    
    with open(user_file, 'w') as f:
        json.dump(user_data, f)
    save_history(user.id, "change_password", "Пароль изменен")
    
    return {
        "message": "Пароль изменен",
        "new_session_token": user_data['session_token']
    }