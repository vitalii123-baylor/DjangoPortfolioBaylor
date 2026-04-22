"""
Lightweight sentiment analysis using rule-based scoring when transformers
are not available, with optional HuggingFace upgrade.
"""
import re
from collections import Counter

POSITIVE_WORDS = {
    'amazing', 'awesome', 'excellent', 'great', 'good', 'love', 'best', 'fantastic',
    'incredible', 'wonderful', 'brilliant', 'outstanding', 'perfect', 'happy', 'excited',
    'thrilled', 'revolutionary', 'innovative', 'powerful', 'helpful', 'beneficial',
    'opportunity', 'democratize', 'accessible', 'hope', 'promising', 'efficient',
    'productive', 'beautiful', 'creative', 'transforming', 'saving', 'improved',
    'recommend', 'grateful', 'dream', 'achieve', 'enjoy', 'celebrate', 'win',
    'success', 'growth', 'advance', 'discover', 'boost', 'profit', 'wealth',
}

NEGATIVE_WORDS = {
    'terrible', 'awful', 'bad', 'horrible', 'worst', 'hate', 'disgusting', 'broken',
    'scam', 'fraud', 'dangerous', 'scary', 'worried', 'concern', 'problem', 'issue',
    'destroying', 'killing', 'replace', 'lost', 'lose', 'fear', 'threat', 'bias',
    'unfair', 'inequality', 'crisis', 'exploit', 'predatory', 'trap', 'nightmare',
    'devastat', 'bankrupt', 'debt', 'collapse', 'bubble', 'fail', 'overwhelm',
    'anxiety', 'stress', 'burnout', 'toxic', 'manipulate', 'spy', 'surveillance',
    'misinformation', 'fake', 'hallucin', 'unreliable', 'confused', 'mess',
}

STOP_WORDS = {
    'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
    'may', 'might', 'shall', 'can', 'need', 'dare', 'ought', 'used',
    'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'you', 'your', 'he', 'she',
    'it', 'they', 'them', 'what', 'which', 'who', 'this', 'that', 'these', 'those',
    'and', 'but', 'or', 'nor', 'for', 'yet', 'so', 'at', 'by', 'of', 'in', 'on',
    'to', 'up', 'as', 'into', 'with', 'about', 'than', 'then', 'just', 'more',
    'also', 'very', 'really', 'too', 'much', 'many', 'most', 'some', 'any',
    'all', 'both', 'each', 'few', 'other', 'such', 'no', 'not', 'only',
    'same', 'so', 'than', 'too', 'very', 's', 't', 'will', 'now',
}


def _score_text(text: str) -> tuple[str, float]:
    words = re.findall(r'\b[a-z]+\b', text.lower())
    pos = sum(1 for w in words if any(w.startswith(pw) for pw in POSITIVE_WORDS))
    neg = sum(1 for w in words if any(w.startswith(nw) for nw in NEGATIVE_WORDS))

    total = pos + neg
    if total == 0:
        return 'neutral', 0.55
    score = pos / total
    if score >= 0.6:
        return 'positive', round(0.6 + score * 0.4, 3)
    elif score <= 0.4:
        return 'negative', round(0.6 + (1 - score) * 0.4, 3)
    else:
        return 'neutral', 0.55


def analyze_posts(posts: list[str]) -> list[dict]:
    try:
        from transformers import pipeline
        pipe = pipeline(
            'text-classification',
            model='distilbert-base-uncased-finetuned-sst-2-english',
            truncation=True,
            max_length=512,
        )
        results = []
        for text in posts:
            out = pipe(text[:512])[0]
            label = out['label'].lower()
            conf = out['score']
            if label == 'positive':
                sentiment = 'positive'
            elif label == 'negative':
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            results.append({'text': text, 'sentiment': sentiment, 'confidence': round(conf, 3)})
        return results
    except Exception:
        results = []
        for text in posts:
            sentiment, confidence = _score_text(text)
            results.append({'text': text, 'sentiment': sentiment, 'confidence': confidence})
        return results


def extract_keywords(posts: list[str], topic: str, top_n: int = 20) -> list[str]:
    all_words = []
    topic_words = set(topic.lower().split())
    for text in posts:
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        all_words.extend(w for w in words if w not in STOP_WORDS and w not in topic_words)
    counter = Counter(all_words)
    return [word for word, _ in counter.most_common(top_n)]
