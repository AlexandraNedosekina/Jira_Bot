import requests
from requests.auth import HTTPBasicAuth
import json

def authentication(email, apitoken):
    url = "https://dimamolodec.atlassian.net/rest/api/3/myself"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, apitoken))
    data = response.json()
    return [data["accountId"], data["displayName"]]

def get_issue_types(email, apitoken):
    url = "https://dimamolodec.atlassian.net/rest/api/3/project/TJ"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url,headers=headers,auth=HTTPBasicAuth(email, apitoken))
    data = response.json()
    result=[]
    for types in data["issueTypes"]:
        if not types['subtask']:
            result.append(types["name"])
    return result

def get_assigneeID(email, apitoken, name):
    url="https://dimamolodec.atlassian.net/rest/api/2/users/search"
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response=requests.get(url,headers=headers,auth=(email, apitoken))
    data = response.json()
    for users in data:
        if users["displayName"] == name:
            return[users["accountId"], users["displayName"]]
    return []

def create_issue(email, apitoken,summary, description, issuetype, priority, dateList, assigneeID):
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
                "id": priority 
            },
            "duedate": duedate,#год-месяц-день
            "assignee": {
                "id": assigneeID
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
                "id": priority  
            },
            "assignee": {
                "id": assigneeID
            }
        }
        }
        )
    response=requests.post(url,headers=headers,data= payload,auth=HTTPBasicAuth(email, apitoken))
    data = response.json()
    return(data['key'])

def add_attachments(email, token, issue, file, path):
    url=f"https://dimamolodec.atlassian.net/rest/api/3/issue/{issue}/attachments"
    headers={
    "Accept": "application/json",
    "X-Atlassian-Token": "no-check"
    }

    files={
        "file" : (file, open(path,"rb"), "application-type")
    }

    requests.post(url,headers=headers,auth=(email, token),files=files)