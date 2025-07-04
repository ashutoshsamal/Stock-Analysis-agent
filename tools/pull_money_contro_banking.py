import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/banking/"
url2="https://www.businesstoday.in/bt-tv/market-today"
url3="https://www.businesstoday.in/markets/company-stock"
url4="https://www.businesstoday.in/markets/stocks"
response = requests.get(url4)
soup = BeautifulSoup(response.content, "html.parser")
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
