import requests
import json
import io

auth=("najdenov773@gmail.com", "k5TH4teflUfNRFQcJunw844C")

def search_user(userID):
    with io.open("bot\\bd.csv","r",encoding="utf-8")as f1:
        user_data = f1.read()
        f1.close()
    data=list()
    user_data=user_data.split("\n")
    for users in user_data:
        userTgID=users.split(",")[0]
        displayName=users.split(",")[1]
        userJiraID=users.split(",")[2]
        if userTgID == userID:
            data.append(displayName)
            data.append(userJiraID)
            return data
        else:
            return None