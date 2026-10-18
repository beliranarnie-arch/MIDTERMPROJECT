
import requests

url = "https://jasminerose-2.onrender.com"

try:
    response = requests.get(url, timeout=60)

    print("========== CLASSMATE API ==========")
    print("Status Code:", response.status_code)

    if response.status_code == 200:
        print("API Response:")
        print(response.text)
        print("Successfully accessed classmate's API!")
    else:
        print("Request failed.")
        print(response.text)

except requests.exceptions.RequestException as e:
    print("Connection error:", e)
