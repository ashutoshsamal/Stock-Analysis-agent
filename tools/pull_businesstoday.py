import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool


# bankingnews = "https://www.moneycontrol.com/banking/"
# todaynews="https://www.businesstoday.in/bt-tv/market-today"
# companynews="https://www.businesstoday.in/markets/company-stock"
# stocksnews="https://www.businesstoday.in/markets/stocks"
# stocksnews2="https://www.moneycontrol.com/news/business/stocks/"


@tool
def get_topic_news()->str:
    """
    Fetches and aggregates raw financial news content from multiple predefined news listing or article pages via web scraping.
    This tool scrapes text from various supported financial news sources and concatenates the results into a single string.
    Each source's content is separated by the keyword 'new_source_<topic>' to indicate boundaries between different articles or sections.
    It is designed to be called without parameters to collect all raw news content in one go.

    Each section of content is separated using a standardized delimiter:
    new_source_<topic>
    Examples:
        new_source_banking
        new_source_stock
        new_source_company

These markers allow downstream agents to identify which topic the scraped content belongs to.
    Note:
    - This tool is not responsible for filtering or summarizing.
    - Should be used by an agent that calls it and summarizes the combined results.
    """

    URLS={"bankingnews":"https://www.moneycontrol.com/banking/",
          "todaymarket":"https://www.businesstoday.in/bt-tv/market-today",
          "stocknews1":"https://www.businesstoday.in/markets/company-stock",
          "stocknews2":"https://www.businesstoday.in/markets/stocks",
          "stocknews3":"https://www.moneycontrol.com/news/business/stocks/"
          # "stocknews4":"https://economictimes.indiatimes.com/markets/stocks/recos/"
          }
    result = []
    for key in URLS:
        url=URLS[key]
        result.append(f"new_source_{key}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup.prettify())
        tags=soup.find_all('h2')
        # print(tags)
        for tag in tags :

            heading="heading:"+tag.text

            result.append(heading)

            for s in tag.find_next_siblings():
                if s.name=='p':
                    contents="content:"+s.text
                    result.append(contents)
                else:
                    break
    return str(result)

# print(get_topic_news())
# import feedparser
# url="https://b2b.economictimes.indiatimes.com/rss/recentstories"
# x=feedparser.parse(url)
# print(x)
