import requests
import json
import io

url="https://dimamolodec.atlassian.net/rest/api/3/issue/TJ-39/comment/10003"

headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}

response = requests.delete(url,headers=headers, auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
print(response.text)
