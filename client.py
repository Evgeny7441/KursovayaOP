import requests
import json
from pydantic import BaseModel
import re
import time
import hashlib


class User(BaseModel):
    login: str
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


def print_error(response):
    error_data = json.loads(response)
    error = error_data.get("detail", "Ошибка")
    print(f"Ошибка: {error}")


class Client:
    def __init__(self):
        self.session_token = None
    
    def create_signature(self, data):
        current_time = str(int(time.time()))
        body_str = json.dumps(data) if data is not None else "{}"
        signature = hashlib.sha256(f"{self.session_token}{body_str}{current_time}".encode()).hexdigest()
        return signature
    
    def send_request(self, method, url, data=None):
        headers = {'Authorization': self.create_signature(data)}
        
        if method.upper() == 'GET':
            response = requests.get(url, json=data, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PATCH':
            response = requests.patch(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, json=data, headers=headers)
        
        return response.text, response.status_code
    
    def reg(self):
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
            self.session_token = user['session_token']
            print(f"\nПользователь {user['login']} успешно зарегистрирован")
            return True
        else:
            error = response.json().get('detail', 'Ошибка')
            print(f"Произошла ошибка: {error}")
            return False
    
    def auth(self):
        print("\nАВТОРИЗАЦИЯ")
        login = input("Логин: ")
        password = input("Пароль: ")
        
        user_data = AuthUser(login=login, password=password)
        
        response = requests.post("http://localhost:8000/users/auth", json=user_data.model_dump())
        
        if response.status_code == 200:
            user = response.json()
            self.session_token = user['session_token']
            print(f"\nАвторизация {user['login']} прошла успешно")
            return True
        else:
            error = response.json().get('detail', 'Ошибка')
            print(f"Произошла ошибка: {error}")
            return False
    
    def send_array(self):
        array_input = input("Введите числа через пробел: ")
        array = [int(x) for x in array_input.split()]
        if not array:
            print("Ошибка: массив не может быть пустым")
            return
        data = {"array": array}
        result, code = self.send_request('POST', "http://localhost:8000/array/input", data)
        if code == 200:
            response_data = json.loads(result)
            print(response_data['message'])
            print(f"{response_data['array']}")
        else:
            print_error(result)
    
    def generate_random_array(self):
        data = {}
        result, code = self.send_request('POST', "http://localhost:8000/array/generate", data)
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
            print(f"{response_data['array']}")
        else:
            print_error(result)
    
    def get_sorted_array(self):
        result, code = self.send_request('GET', "http://localhost:8000/array/get")
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
            print(response_data['array'])
        else:
            print_error(result)
    
    def get_array_part(self):
        start = int(input("Начальный индекс: "))
        end = int(input("Конечный индекс: "))
        data = {"start": start, "end": end}
        result, code = self.send_request('GET', "http://localhost:8000/array/part", data)
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
            print(response_data['array'])
        else:
            print_error(result)
    
    def sort_current_array(self):
        data = {}
        result, code = self.send_request('POST', "http://localhost:8000/array/sort", data)
        if code == 200:
            response_data = json.loads(result)
            print(response_data['message'])
            print(f"{response_data['array']}")
        else:
            print_error(result)
    
    def delete_array(self):
        result, code = self.send_request('DELETE', "http://localhost:8000/array/delete")
        if code == 200:
            response_data = json.loads(result)
            print(response_data['message'])
            print(f"{response_data['array']}")
        else:
            print_error(result)
    
    def add_elements_to_array(self):
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
        
        result, code = self.send_request('PATCH', "http://localhost:8000/array/addelement", data)
        
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
            print(f"{response_data['array']}")
        else:
            print_error(result)
    
    def view_history(self):
        result, code = self.send_request('GET', "http://localhost:8000/users/history")
        
        if code == 200:
            response_data = json.loads(result)
            print(f"{response_data['message']}")
            history = response_data['history']
            if history == []:
                print("История пуста")
            else:
                for inf in history:
                    print(f"- {inf.get('time')}: {inf.get('operation')} ({inf.get('details')})")
        else:
            print_error(result)
    
    def delete_history(self):
        confirm = input("Вы точно хотите удалить историю? (да/нет): ")
        if confirm.lower() != 'да':
            print("Отмена")
            return
        
        result, code = self.send_request('DELETE', "http://localhost:8000/users/history")
        
        if code == 200:
            response_data = json.loads(result)
            print(response_data['message'])
        else:
            print_error(result)
    
    def change_password(self):
        print("\nСМЕНА ПАРОЛЯ")
        confirm = input("Вы точно хотите изменить пароль? (да/нет): ")
        if confirm.lower() != 'да':
            print("Отмена")
            return
        old_password = input("Старый пароль: ")
        new_password = input("Новый пароль: ")
        if not validate_password(new_password):
            return
        confirm_password = input("Повторите новый пароль: ")
        if new_password != confirm_password:
            print("Ошибка: Пароли не совпадают")
            return
        data = {"old_password": old_password, "new_password": new_password}
        result, code = self.send_request('PATCH', "http://localhost:8000/users/password", data)
        
        if code == 200:
            response_data = json.loads(result)
            self.session_token = response_data['new_session_token']
            print(response_data['message'])
        else:
            print_error(result)
    
    def work_array(self):
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
            try:
                choice = int(input("Выберите действие: "))
                
                match choice:
                    case 1:
                        self.send_array()
                    case 2:
                        self.generate_random_array()
                    case 3:
                        self.get_sorted_array()
                    case 4:
                        self.get_array_part()
                    case 5:
                        self.sort_current_array()
                    case 6:
                        self.delete_array()
                    case 7:
                        self.add_elements_to_array()
                    case 8:
                        return
                    case _:
                        print("Нет такого выбора")           
            except ValueError:
                print("Ошибка корректности ввода")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
    
    def account_management(self):
        while True:
            print("\nУПРАВЛЕНИЕ УЧЕТНОЙ ЗАПИСЬЮ")
            print("1 - История запросов")
            print("2 - Удалить историю запросов")
            print("3 - Сменить пароль")
            print("4 - Назад")
            try:
                choice = int(input("Ваш выбор: "))
                            
                match choice:
                    case 1:
                        self.view_history()
                    case 2:
                        self.delete_history()
                    case 3:
                        self.change_password()
                    case 4:
                        return
                    case _:
                        print("Нет такого выбора")
            except ValueError:
                print("Ошибка корректности ввода")
            except Exception as e:
                print(f"Произошла ошибка: {e}")
    
    def main_menu(self):
        while True:
            print("\nГЛАВНОЕ МЕНЮ")
            print("1 - Работа с массивом")
            print("2 - Управление учетной записью")
            print("3 - Выход из профиля")
            try:
                choice = int(input("Ваш выбор: "))
                          
                match choice:
                    case 1:
                        self.work_array()
                    case 2:
                        self.account_management()
                    case 3:
                        print("Выход из профиля выполнен")
                        self.session_token = None
                        break
                    case _:
                        print("Нет такого выбора")       
            except ValueError:
                print("Некорректный ввод!")
            except Exception as e:
                print(f"Произошла ошибка: {e}")


def main():
    client = Client()
    
    while True:
        print("\nДобро пожаловать в 'Гномью сортировку'!")
        print("1 - Регистрация")
        print("2 - Авторизация")
        print("3 - Выйти из программы")
        try: 
            choice = int(input("Ваш выбор: "))
            
            match choice:
                case 1:
                    if client.reg():
                        client.main_menu()
                case 2:
                    if client.auth():
                        client.main_menu()
                case 3:
                    print("Конец")
                    break
                case _:
                    print("Нет такого выбора")         
        except ValueError:
            print("Некорректный ввод!")
        except Exception as e:
            print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    main()