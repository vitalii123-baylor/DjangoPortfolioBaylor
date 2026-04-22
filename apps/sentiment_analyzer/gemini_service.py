from django.conf import settings
from google import genai

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def generate_sentiment_insights(topic: str, stats: dict, keywords: list) -> str:
    kw_str = ', '.join(keywords[:10]) if keywords else 'N/A'
    prompt = f"""Analyze this sentiment data for "{topic}":
Stats: {stats}
Keywords: {kw_str}

Provide a strategic summary (3-4 sentences) explaining what this means for the market/industry. 
Use professional but engaging language with 1-2 relevant emojis."""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "503" in error_msg:
            # Премиальная заглушка при отсутствии токенов
            return f"[AI_LIMIT_REACHED] :: Strategic Backup Analysis for {topic}: The current trend shows a {stats['positive_pct']}% positive resonance. Based on keywords like {kw_str}, the market displays strong engagement with some underlying volatility. Long-term outlook remains stable under current signal patterns. 🤖📈"
        return f"Analysis feed offline. ({error_msg})"
