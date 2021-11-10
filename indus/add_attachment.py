import requests
import json
import io

url="https://dimamolodec.atlassian.net/rest/api/3/issue/TJ-28/attachments"
headers={
    "Accept": "application/json",
    "X-Atlassian-Token": "no-check"
}

files={
    "file" : ("userlist.csv", open("userlist.csv","rb"), "application-type")
}

response=requests.post(url,headers=headers,auth=("najdenov773@gmail.com", "hBUhBdqwqwVH90NgAOds8AE9"),files=files)
print(response.text) 