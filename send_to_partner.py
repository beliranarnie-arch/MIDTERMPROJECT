
import requests

PARTNER_API_URL = "https://jasminerose-2.onrender.com/api/students"

practice_record = {
    "student_id": "EXT-ARNIE-001",
    "name": "Sample Exchange Record",
    "program": "BSIT",
    "year": 1,
    "section": "A",
    "source": "Partner API"
}

try:
    response = requests.post(
        PARTNER_API_URL,
        json=practice_record,
        timeout=15
    )

    print("Partner API URL:", PARTNER_API_URL)
    print("Status Code:", response.status_code)
    print("Response:", response.text)

except requests.RequestException as error:
    print("Unable to send the record:", error)
