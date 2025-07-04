import requests
from bs4 import BeautifulSoup

url = "https://www.moneycontrol.com/news/business/stocks/"
response = requests.get(url)

soup = BeautifulSoup(response.content, "lxml")
# print(soup.prettify())
tags=soup.find_all('p')
for tag in tags :
    if (str(type(tag.string)) == "<class 'bs4.element.NavigableString'>"
            and len(tag.string) > 35):
        print(tag.string)
# news_section = soup.find('section', class_='startup-news section')
#
# news_headlines = []
# for news_item in news_section.find_all('h3', class_='related_des'):
#     headline = news_item.text.strip()
#     news_headlines.append(headline)
#
# for i, headline in enumerate(news_headlines, start=1):
#     print(f"{i}. {headline}")