import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from apps.sentiment_analyzer.gemini_service import _get_client

def home(request):
    return render(request, 'core/home.html')

def projects(request):
    project_list = [
        {
            'title': 'Smart Expense Tracker',
            'desc': 'AI-driven financial management with automatic expense categorization and insights.',
            'url': '/api/expenses/dashboard/',
            'icon': '💰',
            'tech': ['Django', 'React', 'Gemini AI']
        },
        {
            'title': 'AI Sentiment Analyzer',
            'desc': 'Analyze public opinion on any topic using ML and generative AI synthesis.',
            'url': '/api/sentiment/dashboard/',
            'icon': '📊',
            'tech': ['ML', 'Python', 'Gemini AI']
        },
        {
            'title': 'Cyber-Security Bot',
            'desc': 'A personalized AI assistant trained on professional profile and security concepts.',
            'url': '#',
            'icon': '🛡️',
            'tech': ['NLP', 'Gemini AI']
        }
    ]
    return render(request, 'core/projects.html', {'projects': project_list})

@require_POST
def chat_ask(request):
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '')
        
        prompt = f"""You are "Vitalii-Bot v1.0", a high-tech AI digital assistant for Vitalii's professional portfolio.
Your mission is to provide information about Vitalii (a Cybersecurity Master's student and Software Developer).
CONTEXT: Education at Baylor (MSIS), Stack (Python, React, Django), Focus on Security Analytics & Data Viz.

USER QUERY: "{user_msg}"
RESPONSE:"""

        client = _get_client()
        response = client.models.generate_content(model='gemini-2.5-flash-lite', contents=prompt)
        return JsonResponse({'answer': response.text.strip()})
    except Exception as e:
        error_msg = str(e)
        # Обработка лимитов и перегрузки
        if "429" in error_msg or "quota" in error_msg.lower() or "503" in error_msg:
            return JsonResponse({'answer': "[AI_STANDBY_MODE] :: Tokens exhausted or system high demand. Please wait for cycle refresh. Briefly: Vitalii is a MSIS student at Baylor University specializing in Cyber Security and Python. 🛡️"})
        
        # Общий fallback
        return JsonResponse({'answer': "System running in legacy mode. Vitalii is a MSIS student at Baylor specializing in Cyber Security and Software Development. 🤖"})

def signup(request):
    return redirect('home')
