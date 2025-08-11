import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool

@tool
def get_news():
    """
    This tool scrapes top headlines and detailed news content related to the stock market, companies, economy, and business
    published today on Moneycontrol.com. It is designed to provide real-time news data for downstream summarisation and analysis
    agents in a financial trading system.
    """

    url = "https://www.moneycontrol.com/news/business/stocks/"
    response = requests.get(url)

    soup = BeautifulSoup(response.content, "lxml")
    # print(soup.prettify())
    tags=soup.find_all('p')
    news=[]
    for tag in tags :
        if (str(type(tag.string)) == "<class 'bs4.element.NavigableString'>"
                and len(tag.string) > 35):
            news.append(tag.string)
            news.append("###")
    return str(news)
