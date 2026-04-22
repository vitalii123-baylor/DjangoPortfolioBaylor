import json
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import SentimentSearch, SentimentResult, SocialPost
from .demo_data import get_demo_posts
from .sentiment_ml import analyze_posts, extract_keywords
from .gemini_service import generate_sentiment_insights
from .news_service import fetch_real_news

def get_demo_user():
    return User.objects.filter(is_superuser=True).first() or User.objects.first()

def dashboard(request):
    user = get_demo_user()
    searches = SentimentSearch.objects.filter(user=user).select_related('result').order_by('-created_at')[:10]
    latest_result = None
    if searches.exists():
        try:
            latest_result = searches[0].result
        except SentimentResult.DoesNotExist:
            pass
    context = {
        'searches': searches,
        'latest_result': latest_result,
        'suggested_topics': ['AI', 'Cybersecurity', 'Finance', 'Tesla', 'Bitcoin', 'Nvidia'],
    }
    return render(request, 'sentiment_analyzer/dashboard.html', context)

@require_POST
def analyze(request):
    try:
        user = get_demo_user()
        data = json.loads(request.body)
        topic = data.get('topic', '').strip()
        if not topic:
            return JsonResponse({'error': 'Please enter a topic'}, status=400)

        real_news = fetch_real_news(topic)
        if real_news:
            posts_data = real_news
            posts_text = [p['text'] for p in real_news]
            data_source = 'real_news'
        else:
            demo_posts = get_demo_posts(topic)
            posts_text = demo_posts
            posts_data = [{"text": t, "url": "#", "source": "Demo_Node"} for t in demo_posts]
            data_source = 'demo'

        analyzed = analyze_posts(posts_text)
        pos = [p for p in analyzed if p['sentiment'] == 'positive']
        neg = [p for p in analyzed if p['sentiment'] == 'negative']
        total = len(analyzed)
        pos_pct = round(len(pos) / total * 100, 1)
        neg_pct = round(len(neg) / total * 100, 1)
        neu_pct = round(100 - pos_pct - neg_pct, 1)
        keywords = extract_keywords(posts_text, topic, top_n=20)

        # Gemini Insights (выдаст заглушку внутри, если токены кончились)
        ai_analysis = generate_sentiment_insights(topic, {'total': total, 'positive_pct': pos_pct, 'negative_pct': neg_pct, 'neutral_pct': neu_pct}, keywords)

        search = SentimentSearch.objects.create(user=user, topic=topic)
        result = SentimentResult.objects.create(
            search=search,
            positive_percentage=pos_pct,
            negative_percentage=neg_pct,
            neutral_percentage=neu_pct,
            total_posts_analyzed=total,
            positive_count=len(pos),
            negative_count=len(neg),
            neutral_count=total - len(pos) - len(neg),
            top_keywords=keywords,
            ai_analysis=ai_analysis,
        )

        processed_posts = []
        for i, p in enumerate(analyzed[:15]):
            source_info = posts_data[i]
            SocialPost.objects.create(
                result=result, content=p['text'], sentiment=p['sentiment'],
                confidence=p['confidence'], source=source_info['source']
            )
            processed_posts.append({
                'text': p['text'][:300], 'sentiment': p['sentiment'],
                'confidence': round(p['confidence'], 2), 'source': source_info['source'],
                'url': source_info.get('url', '#')
            })

        return JsonResponse({
            'search_id': search.id,
            'topic': topic,
            'positive_pct': pos_pct,
            'negative_pct': neg_pct,
            'neutral_pct': neu_pct,
            'total': total,
            'ai_analysis': ai_analysis,
            'top_posts': processed_posts,
            'source_type': data_source
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def result_detail(request, pk):
    user = get_demo_user()
    result = get_object_or_404(SentimentResult, pk=pk, search__user=user)
    posts = result.posts.all()[:15]
    return JsonResponse({
        'topic': result.search.topic,
        'positive_pct': float(result.positive_percentage),
        'negative_pct': float(result.negative_percentage),
        'neutral_pct': float(result.neutral_percentage),
        'ai_analysis': result.ai_analysis,
        'posts': [
            {'text': p.content[:300], 'sentiment': p.sentiment, 'confidence': float(p.confidence), 'source': p.source}
            for p in posts
        ],
    })
