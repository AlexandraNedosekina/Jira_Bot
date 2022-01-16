import requests
import json

url="https://jira.66bit.ru/jira/rest/api/2/issue"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}
payload=json.dumps({
   "fields": {
      "project":
      {
         "key": "TJ"
      },
      "summary": 'Тест',
      "description": 'Тест1',
      "issuetype": {
         "id": "10200"#Научиться забирать
      },
      "priority": {
         "id": "2"  #1=highest 2=hight 3=medium 4=low 5=lowest
      },
      "assignee": {
          "name":"masshau"
      },
      "aggregatetimeoriginalestimate": 590400
   }
}
)
response=requests.post(url,headers=headers,data= payload,auth=("Yina-ship-it", "lamata13"))
print(response.text)