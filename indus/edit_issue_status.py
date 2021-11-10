import requests
import json

url="https://dimamolodec.atlassian.net/rest/api/3/issue/TJ-39/transitions"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}
payload=json.dumps(
    {
        "transition": {
            "id": "11"#21 31
        }
    }
)
response=requests.post(url,headers=headers,data=payload,auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
print(response.text)