import requests
import json
import io

url="https://dimamolodec.atlassian.net/rest/api/3/user"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}

with io.open("userlist.csv","r",encoding="utf-8")as f1:
    user_data=f1.read()
    f1.close()
user_data=user_data.split("\n")[0:]
for users in user_data:
    displayname=users.split(",")[0]
    password=users.split(",")[1]
    email=users.split(",")[2]
    name=users.split(",")[2]
    payload=json.dumps(
    {
        "password": password,
        "emailAddress": email,
        "displayName": displayname,
        "name": name
    }
    )
    response=requests.post(url,headers=headers,data= payload,auth=("najdenov773@gmail.com", "egIkQ7wlxJCoNFgFZ2ed1950"))
    print(response.text) 

""" payload=json.dumps(
    {
        "password": "test@1234",
        "emailAddress": "tesuser1@atlassian.com",
        "displayName": "test1 user1",
        "name": "test1user1"
}
)
response=requests.post(url,headers=headers,data= payload,auth=("najdenov773@gmail.com", "egIkQ7wlxJCoNFgFZ2ed1950"))
print(response.text) """