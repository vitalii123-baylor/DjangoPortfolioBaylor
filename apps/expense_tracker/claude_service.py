import json
from django.conf import settings
from google import genai

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def categorize_expense(text: str) -> dict:
    prompt = f"""Analyze the following expense and return ONLY valid JSON (no markdown, no explanation):
"{text}"

Return JSON with these fields:
- category: one of (Food/Drinks, Transport, Entertainment, Subscriptions, Health, Clothing, Housing, Other)
- subcategory: specific subcategory (e.g., Coffee, Gas, Netflix)
- amount: numeric amount if mentioned in text, otherwise null
- is_necessary: true or false (is this expense necessary?)
- advice: short tip in English (1-2 sentences with emoji)

ONLY JSON, nothing else."""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        raw = response.text.strip()
        if raw.startswith('```'):
            parts = raw.split('```')
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith('json'):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        return {
            'category': 'Other',
            'subcategory': '',
            'amount': None,
            'is_necessary': True,
            'advice': f'Could not analyze expense. ({e})'
        }


def parse_receipt_image(image_bytes: bytes, mime_type: str) -> list:
    from google.genai import types
    prompt = """Look at this grocery receipt/check image and extract all purchased items with prices.

Return ONLY a valid JSON array, no markdown, no explanation:
[{"name": "item name", "amount": 4.99, "category": "Food & Drinks"}, ...]

Rules:
- Include every individual line item that has a price
- amount must be a positive number (no currency symbols)
- category: one of Food & Drinks, Transport, Entertainment, Subscriptions, Health, Clothing, Housing, Other
- Skip tax, tip, subtotal, total, discount lines — only product items
- If not a receipt or unreadable, return []
- Return ONLY the JSON array, nothing else"""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                types.Part.from_text(prompt)
            ]
        )
        raw = response.text.strip()
        if raw.startswith('```'):
            parts = raw.split('```')
            raw = parts[1] if len(parts) > 1 else raw
            if raw.startswith('json'):
                raw = raw[4:]
        items = json.loads(raw.strip())
        return items if isinstance(items, list) else []
    except Exception:
        return []


def generate_daily_advice(expenses_summary: str) -> str:
    prompt = f"""You are a friendly financial advisor. Here is a summary of this user's expenses this month:

{expenses_summary}

Give a personalized financial tip in English (3-5 sentences) with specific saving recommendations.
Use a friendly tone and emojis. Start with "I noticed..."."""

    try:
        client = _get_client()
        response = client.models.generate_content(
            model='gemini-2.5-flash-lite',
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f'Daily advice is temporarily unavailable. Keep tracking your expenses! 💪 ({e})'
