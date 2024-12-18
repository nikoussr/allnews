import requests
from configs import NEWS_API_KEY


def fetch_news(country="us", category="general"):
    url = (f"https://newsapi.org/v2/top-headlines?country={country}&apiKey={NEWS_API_KEY}")
    response = requests.get(url)
    print(response.status_code)
    if response.status_code == 200:
        return response.json().get("articles", [])
    return []
