import requests
import json

from requests.api import patch

url="https://dimamolodec.atlassian.net/rest/api/2/users/search"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}
response=requests.get(url,headers=headers,auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
data = response.json()
for users in data:
    if users["accountType"] != "app" and users["active"]:
        print(users["displayName"] + " " + users["accountId"])
