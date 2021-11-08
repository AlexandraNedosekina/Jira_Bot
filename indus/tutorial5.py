import requests
import json
import io

url="https://dimamolodec.atlassian.net/rest/api/3/issue/TJ-36/comment"
headers={
    "Accept": "application/json",
    "Content-Type": "application/json"
}


response=requests.get(url,headers=headers,auth=("najdenov773@gmail.com", "hBUhBdqwqwVH90NgAOds8AE9"))
data = response.json() 
print(data["total"])#получение количества комментариев под задачей
#print(data["comments"][0])#обратиться к первому комментарию
print(data["comments"][0]["body"]["content"][0]["content"][0]["text"])#посмотреть текст комментария
with io.open("comment.csv","w",encoding="utf-8")as f1:
    f1.write("comment id"+ "," + "comment text" + "\n")
    for comments in data["comments"]:
        f1.write(comments["id"] + "," + comments["body"]["content"][0]["content"][0]["text"]+"\n")
    f1.close()#заполнение бд