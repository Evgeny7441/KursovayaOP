import requests
import json
from pydantic import BaseModel
from typing import Union
import re
import hashlib
import time

session_token = None
   
class User(BaseModel):
    login:str
    email: str
    password: str


class AuthUser(BaseModel):
    login: str
    password: str

# ВАРИАНТ 1: ПОДПИСЬ = СЕССИОННЫЙ ТОКЕН
def get_signature():
    return {"Authorization": session_token}

def print_error(response):
    error = response.json().get("detail", "Ошибка")
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
    login = input("Введите логин: ")
    if not validate_login(login):
        return False
    
    email = input("Введите email: ")
    if not validate_email(email):
        return False
    
    password = input("Введите пароль: ")
    if not validate_password(password):
        return False
    
    confirm_password = input("Повторите пароль: ")
    if password != confirm_password:
        print("Ошибка: Пароли не совпадают")
        return False
    
    print("Пароли совпадают")
    global session_token
    user_data = User(login=login, email=email, password=password)
    
    response = requests.post("http://localhost:8000/users/reg", json=user_data.model_dump())
    
    if response.status_code == 200:
        user = response.json()
        session_token = user['session_token']
        print(f"\nПользователь {user['login']} успешно зарегестрирован")
        return True
    elif response.status_code == 400:
        error = response.json().get('detail', 'Ошибка')
        print(f"Ошибка регистрации: {error}")
        return False
    else:
        print_error(response)
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
    elif response.status_code == 401:
        error = response.json().get('detail', 'Ошибка')
        print(f"Ошибка авторизации: {error}")
        return False
    else:
        print_error(response)
        return False


def sort_arr():
    while True:
        print("\nСОРТИРОВКА МАССИВА")
        print("1 - Передать массив на сервер")
        print("2 - Сгенерировать случайный массив")
        print("3 - Получить отсортированный массив")
        print("4 - Получить часть массива")
        print("5 - Отсортировать текущий массив")
        print("6 - Удалить массив")
        print("7 - Добавить элемент")
        print("8 - Назад")
         
        choice = input("Выберите действие: ")
        
        headers = get_signature()
        
        try:
            match choice:
                case "1":
                    array_input = input("Введите числа через пробел: ")
                    array = [int(x) for x in array_input.split()]
                    response = requests.post("http://localhost:8000/array/input", json={"array": array}, headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        print(result['message'])
                    else:
                        print_error(response)
                        
                case "2":
                    response = requests.post("http://localhost:8000/array/generate/", headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"{result['message']}")
                    else:
                        print_error(response)    
                        
                case "3":
                    response = requests.get("http://localhost:8000/array/get/", headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"{result['message']}")
                        print(result['array'])
                    else:
                        print_error(response)
                    
                case "4":
                    start = int(input("Начальный индекс: "))
                    end = int(input("Конечный индекс: "))
                    response = requests.get(f"http://localhost:8000/array/part/?start={start}&end={end}", headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"{result['message']}")
                        print(result['array'])
                    else:
                        print_error(response)   
                        
                case "5":
                    response = requests.post("http://localhost:8000/array/sort/", headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        print(result['message'])
                    else:
                        print_error(response)
                        
                case "6":
                    response = requests.delete("http://localhost:8000/array/delete/", headers=headers)
                    if response.status_code == 200:
                        result = response.json()
                        print(result['message'])
                    else:
                        print_error(response)
                
                case "7":
                    values_input = input("Введите числа через пробел: ")
                    values = [int(x) for x in values_input.split()]
    
                    data = {"values": values}
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
                        continue
        
                    response = requests.patch("http://localhost:8000/array/addelement/", json=data, headers=headers)
    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"{result['message']}")
                    else:
                        print_error(response)
                        
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
            print("\nВведите команду:")
            command = int(input("1 - Сортировка\n2 - История запросов\n3 - Управление уч.записью\n4 - Выход из профиля\n"))
            
            match command:
                case 1:
                    sort_arr()
                case 2:
                    print("Здесь будет история запросов")
                case 3:
                    print("Здесь будет управление уч.записью")    
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