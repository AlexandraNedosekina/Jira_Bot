import requests
from requests.auth import HTTPBasicAuth
import json

def get_assigneeID(email, apitoken, namep):
    url="https://dimamolodec.atlassian.net/rest/api/2/users/search"
    headers={
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    namep.lower()
    response=requests.get(url,headers=headers,auth=(email, apitoken))
    data = response.json()
    vse={}
    nujnie={}
    for users in data:
        if users['accountType'] == 'app': #and users['active'] == True:
            vse[users['displayName']] = users['accountId']
    print(vse)
    for fullname in list(vse.keys()):
        for name in fullname.split(' '):
            name.lower()
            if name.startswith(namep):
                nujnie[fullname] = vse[fullname]
    return nujnie

print(get_assigneeID('najdenov773@gmail.com','Q746KStEfUGMg1oIc9YE2DCD','M'))

dic={
    'A A': '1',
    'A B': '2',
    'B C': '3',
}
nujnie={}
for fullname in list(dic.keys()):
        for name in fullname.split(' '):
            if name.startswith('A'):
                nujnie[fullname] = dic[fullname]
#print(nujnie)

sdf = '123413'
print(sdf.lower())