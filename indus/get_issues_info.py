import requests
import json
import io

url="https://dimamolodec.atlassian.net/rest/api/3/search"

headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}

query = {
    'jql': 'project = TJ'
}

response = requests.get(url,headers=headers,params=query, auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
data = response.json()

issues = data["issues"]

for issue in issues:
    print("ID: " + issue["id"])
    print("Проект: " + issue["fields"]["project"]["name"])
    print("Задача: " + issue["key"])
    print("Тип: " + issue["fields"]["issuetype"]["name"])
    print("Название: " + issue["fields"]["summary"])
    print("Описание: " + issue["fields"]["description"]["content"][0]["content"][0]["text"])
    print("Приоритет: " + issue["fields"]["priority"]["name"])
    print("Исполнитель: " + issue["fields"]["assignee"]["displayName"])
    print("Статус: " + issue["fields"]["status"]["name"])
    if issue["fields"]["duedate"] != None:
        print("Срок исполнения: " + issue["fields"]["duedate"])
    else:
        print("Нет сроков исполнения")
    print()
print(issues[0])
