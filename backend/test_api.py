import urllib.request
import urllib.parse
import json

req1 = urllib.request.Request('http://localhost:8000/api/auth/login', data=urllib.parse.urlencode({'username':'admin','password':'123'}).encode())
with urllib.request.urlopen(req1) as f:
    token = json.loads(f.read().decode())['access_token']

req2 = urllib.request.Request('http://localhost:8000/api/cash-register/summary', headers={'Authorization': f'Bearer {token}'})
with urllib.request.urlopen(req2) as f:
    print(json.loads(f.read().decode()))
