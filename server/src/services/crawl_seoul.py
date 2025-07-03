import requests
from bs4 import BeautifulSoup

def crawl_seoul_wikipedia() -> None:
    url = "https://ko.wikipedia.org/wiki/서울특별시"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    content_div = soup.find("div", {"class": "mw-parser-output"})
    paragraphs = content_div.find_all("p")

    text_data = "\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

    with open("data/seoul_info.txt", "w", encoding="utf-8") as f:
        f.write(text_data)

    print("크롤링 완료! 텍스트 저장됨.")