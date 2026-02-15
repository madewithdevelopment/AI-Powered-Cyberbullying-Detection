import urllib.request
import json

url = "http://127.0.0.1:5000/api/platform/scan"
data = json.dumps({"platform": "whatsapp"}).encode()
headers = {"Content-Type": "application/json"}
req = urllib.request.Request(url, data=data, headers=headers)

try:
    r = urllib.request.urlopen(req)
    print("OK:", r.read().decode()[:500])
except urllib.error.HTTPError as e:
    print(f"Error {e.code}:")
    body = e.read().decode()
    print(body[:3000])
except Exception as e:
    print(f"Exception: {e}")
