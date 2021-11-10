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
      "summary": "REST ye merry gentlemen.",
      "description": 'Created for test11',
      "issuetype": {
         "name": "Задача"
      },
      "priority": {
         "id": "4"  #1=highest 2=hight 3=medium 4=low 5=lowest
      },
      "duedate": "2022-05-11",#год-месяц-день
      "assignee": {
         "id": "616c5b31bcb5740068e92873"
      }
   }
}
)
response=requests.post(url,headers=headers,data= payload,auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
print(response.text)