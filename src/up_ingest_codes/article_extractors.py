import requests
from bs4 import BeautifulSoup

def extract_khan_article_body(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        content_tags = soup.find_all("p", class_=["content_text text-l","content_text"])
        content_text = "\n\n".join([tag.get_text(strip=True) for tag in content_tags])
        return content_text if content_text else ""
    except Exception as e:
        print(f"❗경향 본문 크롤링 실패: {url} - {e}")
        return ""

def extract_yna_article_body(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        content_div = soup.find("div", class_="story-news article")
        if not content_div:
            content_div = soup.find("div", class_="article")
        content_text = "\n\n".join([p.get_text(strip=True) for p in content_div.find_all("p")])
        return content_text if content_text else ""
    except Exception as e:
        print(f"❗연합 본문 크롤링 실패: {url} - {e}")
        return ""

def extract_mk_article_body(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()

        response = requests.get("https://www.mk.co.kr/news/society/11288848")
        soup = BeautifulSoup(response.text, "html.parser")
        content_tags = soup.find_all("p", attrs={"refid":True})
        text = ""
        for tag in content_tags:
            text += tag.text
        return text if text else ""
    except Exception as e:
        print(f"❗매경 본문 크롤링 실패: {url} - {e}")
        return ""
