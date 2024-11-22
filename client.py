import time

import requests

SERVER_URL = "http://127.0.0.1:5000"

def register_license():
    username = input("Enter username: ")
    password = input("Enter password: ")
    license_type = input("Enter license type (small/large): ")
    response = requests.post(f"{SERVER_URL}/generate_license", json={
        "username": username,
        "password": password,
        "license_type": license_type
    })
    if response.status_code == 200:
        print("License generated:", response.json())
    else:
        print("Error:", response.json())
def use_license():
    serial_key = input("Enter serial key: ")
    response = requests.post(f"{SERVER_URL}/verify_license", json={"serial_key": serial_key})
    if response.status_code == 200:
        print("Access granted!")
        while True:
            requests.post(f"{SERVER_URL}/heartbeat", json={"serial_key": serial_key})
            print("Heartbeat sent...")
            time.sleep(30)
    else:
        print("Access denied:", response.json())

if __name__ == "__main__":
    print("1. Register License")
    print("2. Use License")
    choice = input("Choose an option: ")
    if choice == "1":
        register_license()
    elif choice == "2":
        use_license()