import requests
import json
import io
from configSasha import *

auth=(login, token)

def search_user(userID):
    with io.open("botdokonca\\bd.csv","r",encoding="utf-8")as f1:
        user_data = f1.read()
        f1.close()
    data=list()
    user_data=user_data.split("\n")
    for users in user_data:
        userTgID=users.split(",")[0]
        displayName=users.split(",")[1]
        userJiraID=users.split(",")[2]
        # if userTgID == userID:
        data.append(displayName)
        data.append(userJiraID)
        return data
        # else:
        #     return None

def create_issue(summary, description, issuetype, priority, dateList, assignee):
    idprioryty = '3'
    if priority == "Lowest":
        idprioryty = '5'
    elif priority == "Low":
        idprioryty = '4'
    elif priority == "High":
        idprioryty = '2'
    elif priority == "Highest":
        idprioryty = '1'
    if len(dateList) == 3:
        duedate = dateList[2] + "-" + dateList[1] + "-" + dateList[0]

    url="https://dimamolodec.atlassian.net/rest/api/2/issue"
    headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
    if len(dateList) == 3:
        payload=json.dumps({
            "fields": {
            "project":
            {
                "key": "TJ"
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": issuetype
            },
            "priority": {
                "id": idprioryty  #1=highest 2=hight 3=medium 4=low 5=lowest
            },
            "duedate": duedate,#год-месяц-день
            "assignee": {
                "id": get_user_id(assignee)
            }
        }
        }
        )
    else:
        payload=json.dumps({
            "fields": {
            "project":
            {
                "key": "TJ"
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "name": issuetype
            },
            "priority": {
                "id": idprioryty  #1=highest 2=hight 3=medium 4=low 5=lowest
            },
            "assignee": {
                "id": get_user_id(assignee)
            }
        }
        }
        )
    response=requests.post(url,headers=headers,data= payload,auth=auth)
    print(response.text)
#начало
def get_user_id(displayName):
    url="https://dimamolodec.atlassian.net/rest/api/2/users/search"
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response=requests.get(url,headers=headers,auth=auth)
    data = response.json()
    for users in data:
        if users["displayName"] == displayName:
            return(users["accountId"])
#конец