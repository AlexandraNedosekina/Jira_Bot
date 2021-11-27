import requests
from requests.auth import HTTPBasicAuth

def authentication(email, apitoken):
    url = "https://dimamolodec.atlassian.net/rest/api/3/myself"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, auth=HTTPBasicAuth(email, apitoken))
    result=[]
    try:
        data = response.json()
        try:
            print(data["status-code"])
            result.append('401')
        except:
            result.append(data["accountId"])
            result.append(data["displayName"])
            
    except:
        result.append('401')
    return result

def get_issue_types(email, apitoken):
    url = "https://dimamolodec.atlassian.net/rest/api/3/project/TJ"
    headers = {
        "Accept": "application/json"
    }
    response = requests.get(url,headers=headers,auth=HTTPBasicAuth("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
    data = response.json()
    result=[]
    for types in data["issueTypes"]:
        if not types['subtask']:
            result.append(types["name"])
    return result

    