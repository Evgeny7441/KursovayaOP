import unittest
import requests
import json
import time
import hashlib

class TestAllEndpoints(unittest.TestCase):
    
    def setUp(self):
        self.base_url = "http://127.0.0.1:8000"
        self.username = f"testuser_{int(time.time())}"
        self.email = f"test_{int(time.time())}@test.com"
        self.password = "Test123!@#"
        self.token = None
    
    def _auth_user(self):
        response = requests.post(f"{self.base_url}/users/auth", 
        json={"login": self.username, "password": self.password})
        if response.status_code == 200:
            self.token = response.json().get("session_token")
        return response
    
    def _get_signature(self, body=None):
        if not self.token: 
            return None
        current_time = str(int(time.time()))
        body_str = json.dumps(body) if body else "{}"
        return hashlib.sha256(f"{self.token}{body_str}{current_time}".encode()).hexdigest()
    
    def test_01_registration(self):
        response = requests.post(f"{self.base_url}/users/reg", 
        json={"login": self.username, "email": self.email, "password": self.password})
        
        print(f"\nРегистрация пользователя:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_02_registration_duplicate(self):
        response = requests.post(f"{self.base_url}/users/reg", 
        json={"login": self.username, "email": self.email, "password": self.password})
        
        print(f"\nРегистрация уже зарегистрированного пользователя:")
        print(f"Ожидаемый код: 400")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 400)
    
    def test_03_auth(self):
        response = self._auth_user()
        
        print(f"\nАвторизация пользователя:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_04_auth_wrong(self):
        response = requests.post(f"{self.base_url}/users/auth", 
        json={"login": "wronguser", "password": "wrongpassword"})
        
        print(f"\nАвторизация с неверными данными:")
        print(f"Ожидаемый код: 401")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 401)

    def test_05_array_input_no_auth(self):
        array_data = {"array": [5, 3, 8, 1, 2]}
        headers = {"Authorization": "invalid_signature"}
        response = requests.post(f"{self.base_url}/array/input", json=array_data, headers=headers)
        
        print(f"\nВвод массива без авторизации:")
        print(f"Ожидаемый код: 401")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 401)
    
    def test_06_array_input(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        array_data = {"array": [5, 3, 8, 1, 2]}
        signature = self._get_signature(array_data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/input", json=array_data, headers=headers)
        
        print(f"\nВвод массива:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_07_array_sort(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        array_data = {"array": [5, 3, 8, 1, 2]}
        signature = self._get_signature(array_data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/input", json=array_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        signature = self._get_signature()
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/sort", headers=headers)
        
        print(f"\nСортировка массива:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_08_array_get(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        array_data = {"array": [5, 3, 8, 1, 2]}
        signature = self._get_signature(array_data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/input", json=array_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        signature = self._get_signature()
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/sort", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        response = requests.get(f"{self.base_url}/array/get", headers=headers)
        
        print(f"\nПолучение отсортированного массива:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_09_array_generate(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        signature = self._get_signature()
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/generate", headers=headers)
        
        print(f"\nГенерация случайного массива:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_10_array_delete(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        signature = self._get_signature()
        headers = {"Authorization": signature}
        response = requests.delete(f"{self.base_url}/array/delete", headers=headers)
        
        print(f"\nУдаление массива:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
    
    def test_11_array_add_elements(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        array_data = {"array": [1, 2, 3]}
        signature = self._get_signature(array_data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/input", json=array_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        add_data = {"values": [4, 5], "index": -1, "position": "end"}
        signature = self._get_signature(add_data)
        headers = {"Authorization": signature}
        response = requests.patch(f"{self.base_url}/array/addelement", json=add_data, headers=headers)
        
        print(f"\nДобавление элементов в массив:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)

    def test_12_array_part(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        array_data = {"array": [9, 7, 5, 3, 1]}
        signature = self._get_signature(array_data)
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/input", json=array_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        
        signature = self._get_signature()
        headers = {"Authorization": signature}
        response = requests.post(f"{self.base_url}/array/sort", headers=headers)
        self.assertEqual(response.status_code, 200)
        
        part_data = {"start": 1, "end": 4}
        signature = self._get_signature(part_data)
        headers = {"Authorization": signature}
        response = requests.get(f"{self.base_url}/array/part", json=part_data, headers=headers)
        
        print(f"\nПолучение части массива:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
        
    def test_13_get_history(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        signature = self._get_signature()
        headers = {"Authorization": signature}
        response = requests.get(f"{self.base_url}/users/history", headers=headers)
        
        print(f"\nПолучение истории:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)

    def test_14_delete_history(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)
        
        signature = self._get_signature()
        headers = {"Authorization": signature}
        response = requests.delete(f"{self.base_url}/users/history", headers=headers)
        
        print(f"\nУдаление истории запросов:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
            
    def test_15_change_password(self):
        auth_response = self._auth_user()
        self.assertEqual(auth_response.status_code, 200)

        new_password = "NewTest123!@#"
        change_data = {
            "old_password": self.password,
            "new_password": new_password
        }
        signature = self._get_signature(change_data)
        headers = {"Authorization": signature}
        response = requests.patch(f"{self.base_url}/users/password", json=change_data, headers=headers)
        
        print(f"\nИзменение пароля:")
        print(f"Ожидаемый код: 200")
        print(f"Итог: {response.status_code}")
        self.assertEqual(response.status_code, 200)
            
if __name__ == "__main__":
    unittest.main()