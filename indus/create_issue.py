import requests
import json

url="https://dimamolodec.atlassian.net/rest/api/2/issue"
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
      "summary": 'Реализовать ветвления у исполнителя задачи',
      "description": '',
      "issuetype": {
         "name": "Задача"
      },
      "priority": {
         "id": "2"  #1=highest 2=hight 3=medium 4=low 5=lowest
      },
      "duedate": "2022-11-30",#год-месяц-день
      "assignee": {
         "id": "606b41c0b845ed006e98f901"
      }
   }
}
)
response=requests.post(url,headers=headers,data= payload,auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
print(response.text)