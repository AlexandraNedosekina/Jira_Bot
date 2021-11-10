import requests
import json
import io

url="https://dimamolodec.atlassian.net/rest/api/3/issue/TJ-36/comment"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}

data = json.dumps({
  "body": {
    "type": "doc",
    "version": 1,
    "content": [
      {
        "type": "paragraph",
        "content": [
          {
            "text": "comment 1",
            "type": "text"
          }
        ]
      }
    ]
  }
})
response=requests.post(url,headers=headers,data=data, auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C"))
print(response.text)