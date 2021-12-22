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
        if types['hierarchyLevel'] == 0:
            result.append(types["name"])
    return result

def get_assigneeID(email, apitoken, partname):
    url="https://dimamolodec.atlassian.net/rest/api/2/users/search"
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response=requests.get(url,headers=headers,auth=(email, apitoken))
    data = response.json()
    partname.lower()
    allusers={}
    needusers={}
    for users in data:
        if users['accountType'] == 'atlassian': #and users['active'] == True:
            allusers[users['displayName']] = users['accountId']
    for fullname in list(allusers.keys()):
        for name in fullname.split(' '):
            name.lower()
            if name.startswith(partname):
                needusers[fullname] = allusers[fullname]
    return needusers

def create_issue(email, apitoken,summary, description, issuetype, priority, dateList, assigneeID):
    url="https://dimamolodec.atlassian.net/rest/api/2/issue"
    headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
    }
    issue = {"project":
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
    if len(dateList) == 3:
        duedate = dateList[2] + "-" + dateList[1] + "-" + dateList[0]
        issue["duedate"] = duedate
    payload=json.dumps({"fields": issue})
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