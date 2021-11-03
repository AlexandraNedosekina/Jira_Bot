import requests
import json

from requests.api import patch

url="https://dimamolodec.atlassian.net/rest/api/2/users/search"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}
response=requests.get(url,headers=headers,auth=("najdenov773@gmail.com", "egIkQ7wlxJCoNFgFZ2ed1950"))
data = response.json()
for users in data:
    if users["accountType"] != "app":
        print(users["displayName"] + " " + users["accountId"])
