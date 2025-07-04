import requests
from bs4 import BeautifulSoup

urlnse = "https://www.moneycontrol.com/stocks/marketstats/nsehigh/index.php"
urlbse="https://www.moneycontrol.com/stocks/marketstats/bsehigh/index.php"
response = requests.get(urlbse)
soup = BeautifulSoup(response.content, "html.parser")
# print(soup.prettify())
tags=soup.find_all('tr')

for tag in tags :
    print("####")
    for c in tag.children:
        print(c.text)
