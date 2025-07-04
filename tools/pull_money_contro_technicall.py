import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/news/tags/technical-analysis.html"
response = requests.get(url)

soup = BeautifulSoup(response.content, "lxml")
# print(soup.prettify())
tags=soup.find_all('h2')
# print(tags)
for tag in tags :
    print("####")
    print(tag.text)
    for s in tag.find_next_siblings():
        if s.name=='p':
            print(s.text)
        else:
            print("-----")
            break
    print(type(tag.string))

