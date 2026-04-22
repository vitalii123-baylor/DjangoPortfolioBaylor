import requests
from django.conf import settings

def fetch_real_news(topic: str):
    """
    Fetches real news articles from NewsAPI.ai (Event Registry).
    Uses a small count to save tokens.
    """
    url = "https://eventregistry.org/api/v1/article/getArticles"
    
    params = {
        "action": "getArticles",
        "keyword": topic,
        "articlesPage": 1,
        "articlesCount": 15,
        "articlesSortBy": "date",
        "resultType": "articles",
        "apiKey": settings.NEWS_API_KEY,
        "lang": "eng"
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            articles = data.get("articles", {}).get("results", [])
            
            if not articles:
                return None
            
            # Extract titles and snippets
            news_list = []
            for art in articles:
                text = f"{art.get('title')}. {art.get('body', '')[:200]}"
                news_list.append({
                    "text": text,
                    "url": art.get("url"),
                    "source": art.get("source", {}).get("title", "News Node")
                })
            return news_list
        return None
    except Exception:
        return None
