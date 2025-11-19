import requests
import json
from pydantic import BaseModel
from typing import Union
import re

   
class User(BaseModel):
    login:str
    email: str
    password: str


class AuthUser(BaseModel):
    login: str
    password: str


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
    user_data = User(login=login, email=email, password=password)
    
    response = requests.post("http://localhost:8000/users/reg", json=user_data.model_dump())
    
    if response.status_code == 200:
        user = response.json()
        print(f"\nПользователь {user['login']} успешно зарегестрирован")
        return True
    elif response.status_code == 400:
        error = response.json().get('detail', 'Ошибка')
        print(f"Ошибка регистрации: {error}")
        return False
    else:
        error = response.json().get("detail", "Ошибка")
        print(f"Ошибка: {error}")
        return False


def auth():
    print("\nАВТОРИЗАЦИЯ")
    login = input("Логин: ")
    password = input("Пароль: ")
    
    user_data = AuthUser(login=login, password=password)
    
    response = requests.post("http://localhost:8000/users/auth", json=user_data.model_dump())
    
    if response.status_code == 200: 
        user = response.json()
        print(f"\nАвторизация {user['login']} прошла успешно")
        return True
    elif response.status_code == 401:
        error = response.json().get('detail', 'Ошибка')
        print(f"Ошибка авторизации: {error}")
        return False
    else:
        print(f"Неизвестная ошибка: {response.status_code}")
        return False
       
                      
def sort_arr():
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
    
    match choice:
        case "1":
            print("Ввод массива")
        case "2":
            print("Сгенерировать массив")
        case "3":
            print("Получить отсорт массив")
        case "4":
            print("Часть массива")
        case "5":
            print("Отсортировать массива")
        case "6":
            print("Удаление элемента")
        case "7":
            print("Добавление элемента")
        case "8":
            return
        case _:
            print("Неверная команда!")
               
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