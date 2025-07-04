url="https://www.google.com/finance/quote/TATAMOTORS:NSE"

import requests
from bs4 import BeautifulSoup

ticker ='TATAMOTORS'
url=f'https://www.google.com/finance/quote/{ticker}: '

response=requests.get(url)

soup = BeautifulSoup(response.content, "lxml")

class1="YMlKec fxKbKc"

price=soup.find(class_=class1).text

print(price)
