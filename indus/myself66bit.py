import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://jira.66bit.ru/jira/rest/api/2/myself"
headers = {
        "Accept": "application/json"
}
response = requests.get(url, headers=headers, auth=HTTPBasicAuth('Yina-ship-it', 'lamata13'))
data = response.json()
print(data)