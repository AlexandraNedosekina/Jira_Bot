import requests
import json

url="https://jira.66bit.ru/jira/rest/api/2/issue/TJ-9"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}
response=requests.post(url,headers=headers,auth=("Yina-ship-it", "lamata13"))
print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))