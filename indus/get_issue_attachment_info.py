import requests
from requests.auth import HTTPBasicAuth
import json

url = "https://dimamolodec.atlassian.net/rest/api/3/issue/TJ-39"

auth = HTTPBasicAuth("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C")

headers = {
   "Accept": "application/json"
}

response = requests.get(
   url,
   headers=headers,
   auth=auth
)

data = response.json()
for i in range(0, len(data["fields"]["attachment"])):
    print(data["fields"]["attachment"][i]["filename"])
