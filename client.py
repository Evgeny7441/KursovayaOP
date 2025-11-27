import requests
import json
from pydantic import BaseModel
from typing import Union
import re
import time
import hashlib

session_token = None

class Item(BaseModel): 
    name: str
    description: Union[str, None] = "Описание товара"
    price: float
    id: Union[int, None] = -1
    
    def __str__(self):
        return f"Товар: {self.name}, стоимость: {self.price} рублей"
    
    
class User(BaseModel):
    login:str
    email: str
    password: str


class AuthUser(BaseModel):
    login: str
    password: str   

def create_signature_v4(data):
    global session_token
    current_time = str(int(time.time()))
    body_str = json.dumps(data) if data is not None else "{}"
    signature = hashlib.sha256(f"{session_token}{body_str}{current_time}".encode()).hexdigest()
    return signature

def send_request(method, url, data=None):   
    headers = {'Authorization': create_signature_v4(data)}
    
    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    elif method.upper() == 'PATCH':
        response = requests.patch(url, json=data, headers=headers)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers)
    
    return response.text, response.status_code


def all_items():
    result, code = send_request('GET', "http://localhost:8000/items/print")
    match code:
        case 200:
            json_items = json.loads(result)
            for json_item in json_items:
                item = Item(**json_item)
                print(item)
                
        case 401:
            print("Неверные авторизацинные данные")

        case 403:
            print("Доступ ограничен")
        
        case _:
            print("Неизвестная ошибка")


def create_item():
    print("\nДОБАВЛЕНИЕ ТОВАРА")
    name = input("Название товара: ")
    price = float(input("Цена товара: "))
    
    item_data = Item(name=name, price=price)
    
    result, code = send_request('POST', "http://localhost:8000/items/create", item_data.model_dump())
    
    match code:
        case 200:
            created_item = Item(**json.loads(result))
            print(f"{created_item} добавлен")
            
        case 401:
            print("Неверные авторизацинные данные")

        case 403:
            print("Доступ ограничен")
        
        case _:
            print("Неизвестная ошибка")


def validate_login(login):
    if len(login) < 8:
        print("Ошибка: Логин должен содержать не менее 8 символов")
        return False
    return True

def validate_email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        print("Ошибка: Неверный формат email. Пример: user@gmail.com")
        return False
    return True

def validate_password(password):
    password_pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*(),.?":{}|<>]).{10,}$'
    if not re.match(password_pattern, password):
        print("Ошибка: Пароль должен содержать мин. 10 символов, заглавные/строчные буквы, спецсимволы")
        return False
    return True

def reg():
    global session_token
    print("\nРЕГИСТРАЦИЯ")
    login = input("Логин: ")
    if not validate_login(login):
        return False
    
    email = input("Email: ")
    if not validate_email(email):
        return False
    
    password = input("Пароль: ")
    if not validate_password(password):
        return False
    
    confirm_password = input("Повторите пароль: ")
    if password != confirm_password:
        print("Ошибка: Пароли не совпадают")
        return False
    
    print("Пароли совпадают")
    user_data = User(login=login, email=email, password=password)
    
    response = requests.post("http://localhost:8000/users/reg", json=user_data.model_dump())
    
    if response.status_code == 200:
        user = response.json()
        session_token = user['session_token']
        print(f"\nПользователь {user['login']} успешно зарегестрирован")
        return True
    else:
        error = response.json().get('detail', 'Ошибка')
        print(f"Произошла ошибка: {error}")
        return False


def auth():
    global session_token
    print("\nАВТОРИЗАЦИЯ")
    login = input("Логин: ")
    password = input("Пароль: ")
    
    user_data = AuthUser(login=login, password=password)
    
    response = requests.post("http://localhost:8000/users/auth", json=user_data.model_dump())
    
    if response.status_code == 200:
        user = response.json()
        session_token = user['session_token']
        print(f"\nАвторизация {user['login']} прошла успешно")
        return True
    else:
        error = response.json().get('detail', 'Ошибка')
        print(f"Произошла ошибка: {error}")
        return False
        
               
def main_menu():
    
    while True:
        try:
            print("\nВведите команду:")
            command = int(input("1 - Список товаров\n2 - Добавить товар\n3 - Выйти из профиля\n"))
            
            match command:
                case 1:
                    all_items()
                case 2:
                    create_item()
                case 3:
                    break
                case _:
                    print("Нет такого выбора")
                    
        except ValueError:
            print("Некорректный ввод!")
            
            
while True:
    try:
        print("\nВведите команду:")
        command = int(input("1 - Регистрация\n2 - Авторизация\n3 - Выйти из программы\n"))
        
        match command:
            case 1:
                if reg():
                    main_menu()
            case 2:
                if auth():
                    main_menu()
            case 3:
                print("Конец")
                break
            case _:
                print("Нет такого выбора")
                
    except ValueError:
        print("Некорректный ввод!")