import requests

def run():
    # Login
    resp = requests.post("http://localhost:8000/api/auth/login", data={"username": "officer1", "password": "Password123!"})
    if not resp.ok:
        print("Login failed:", resp.text)
        return
    token = resp.json()["access_token"]
    
    # Get case 31
    headers = {"Authorization": f"Bearer {token}"}
    case = requests.get("http://localhost:8000/api/cases/31", headers=headers)
    print(case.text)

if __name__ == "__main__":
    run()
