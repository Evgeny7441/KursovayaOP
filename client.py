import requests
import json
from pydantic import BaseModel
from typing import Union
import re
import time
import hashlib

session_token = None
    
class User(BaseModel):
    login:str
    email: str
    password: str


class AuthUser(BaseModel):
    login: str
    password: str   

def create_signature(data):
    global session_token
    current_time = str(int(time.time()))
    body_str = json.dumps(data) if data is not None else "{}"
    signature = hashlib.sha256(f"{session_token}{body_str}{current_time}".encode()).hexdigest()
    return signature

def send_request(method, url, data=None):   
    headers = {'Authorization': create_signature(data)}
    
    if method.upper() == 'GET':
        response = requests.get(url, json=data, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    elif method.upper() == 'PATCH':
        response = requests.patch(url, json=data, headers=headers)
    elif method.upper() == 'DELETE':
        response = requests.delete(url, headers=headers)
    
    return response.text, response.status_code

def print_error(response):
    error_data = json.loads(response)
    error = error_data.get("detail", "Ошибка")
    print(f"Ошибка: {error}")

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
        print(f"\nПользователь {user['login']} успешно зарегистрирован")
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
        
               
def send_array():
    array_input = input("Введите числа через пробел: ")
    array = [int(x) for x in array_input.split()]
    if not array:
        print("Ошибка: массив не может быть пустым")
        return
    data = {"array": array}
    result, code = send_request('POST', "http://localhost:8000/array/input/", data)
    if code == 200:
        response_data = json.loads(result)
        print(response_data['message'])
    else:
        print_error(result)

def generate_random_array():
    data = {}
    result, code = send_request('POST', "http://localhost:8000/array/generate/", data)
    if code == 200:
        response_data = json.loads(result)
        print(f"{response_data['message']}")
    else:
        print_error(result)

def get_sorted_array():
    result, code = send_request('GET', "http://localhost:8000/array/get/")
    if code == 200:
        response_data = json.loads(result)
        print(f"{response_data['message']}")
        print(response_data['array'])
    else:
        print_error(result)

def get_array_part():
    start = int(input("Начальный индекс: "))
    end = int(input("Конечный индекс: "))
    data = {"start": start, "end": end}
    result, code = send_request('GET', "http://localhost:8000/array/part/", data)
    if code == 200:
        response_data = json.loads(result)
        print(f"{response_data['message']}")
        print(response_data['array'])
    else:
        print_error(result)

def sort_current_array():
    data = {}
    result, code = send_request('POST', "http://localhost:8000/array/sort/", data)
    if code == 200:
        response_data = json.loads(result)
        print(response_data['message'])
    else:
        print_error(result)

def delete_array():
    result, code = send_request('DELETE', "http://localhost:8000/array/delete/")
    if code == 200:
        response_data = json.loads(result)
        print(response_data['message'])
    else:
        print_error(result)

def add_elements_to_array():
    values_input = input("Введите числа через пробел: ")
    values = [int(x) for x in values_input.split()]
    if not values:
        print("Ошибка: не введены элементы для добавления")
        return
    data = {"values": values, "index": -1}
    add_choice = input("1 - Добавить в начало\n2 - Добавить в конец\n3 - Добавить после индекса\nВаш выбор: ")
    
    if add_choice == "1":
        data["position"] = "start"
    elif add_choice == "2":
        data["position"] = "end"
    elif add_choice == "3":
        index = int(input("Введите индекс: "))
        data["position"] = "after"
        data["index"] = index
    else:
        print("Неверный выбор")
        return
    
    print(data)
    result, code = send_request('PATCH', "http://localhost:8000/array/addelement/", data)
    
    if code == 200:
        response_data = json.loads(result)
        print(f"{response_data['message']}")
    else:
        print_error(result)


def work_array():
    while True:
        print("\nРАБОТА С МАССИВОМ")
        print("1 - Передать массив на сервер")
        print("2 - Сгенерировать случайный массив")
        print("3 - Получить отсортированный массив")
        print("4 - Получить часть массива")
        print("5 - Отсортировать текущий массив")
        print("6 - Удалить массив")
        print("7 - Добавить элемент")
        print("8 - Назад")
        
        choice = input("Выберите действие: ")
        
        try:
            match choice:
                case "1":
                    send_array()
                case "2":
                    generate_random_array()
                case "3":
                    get_sorted_array()
                case "4":
                    get_array_part()
                case "5":
                    sort_current_array()
                case "6":
                    delete_array()
                case "7":
                    add_elements_to_array()
                case "8":
                    return
                case _:
                    print("Нет такого выбора")
                    
        except ValueError:
            print("Ошибка корректности ввода")
        except Exception as e:
            print(f"Произошла ошибка: {e}")
               
def main_menu():
    while True:
        try:
            print("\nГЛАВНОЕ МЕНЮ")
            command = int(input("1 - Работа с массивом\n2 - История запросов\n3 - Управление уч.записью\n4 - Выход из профиля\n"))
            
            match command:
                case 1:
                    work_array()
                case 2:
                    print("История запросов")
                case 3:
                    print("Управление уч.записью")    
                case 4:
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