import requests
import json

url="https://dimamolodec.atlassian.net/rest/api/2/issue"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}
payload=json.dumps(
    {
    "fields": {
       "project":
       {
          "key": "TJ"
       },
       "summary": "REST ye merry gentlemen.",
       "description": 'Created for test11',
       "issuetype": {
          "name": "Задача"
       }
    }
    }
)
response=requests.post(url,headers=headers,data= payload,auth=("najdenov773@gmail.com", "egIkQ7wlxJCoNFgFZ2ed1950"))
print(response.text)