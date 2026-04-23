import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from google import genai

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client

JOBS = [
    {'company': 'Baylor University',        'role': 'Teacher Assistant',       'period': 'Aug 2025 – Present',       'color': 'var(--cyan)'},
    {'company': 'Brazos Innovation Partners','role': 'Software Engineer Intern', 'period': 'Jun 2025 – Jul 2025',      'color': '#4ade80'},
    {'company': 'Upwork',                   'role': 'Full Stack Developer',     'period': 'Mar 2022 – Jan 2025',      'color': 'var(--purple)'},
    {'company': 'JazzTeam',                 'role': 'Full Stack Developer',     'period': 'Mar 2020 – Mar 2022',      'color': 'var(--pink)'},
    {'company': 'Likeit',                   'role': 'Front-end Developer',      'period': 'Aug 2018 – Jan 2020',      'color': 'rgba(255,140,0,0.9)'},
]

def home(request):
    return render(request, 'core/home.html', {'jobs': JOBS})

def projects(request):
    project_list = [
        {
            'title': 'Smart Expense Tracker',
            'desc': 'AI-driven financial management with automatic expense categorization, budget tracking, and personalized spending insights powered by Gemini AI.',
            'url': '/api/expenses/dashboard/',
            'icon': '💰',
            'tech': ['Django', 'Python', 'Gemini AI', 'Chart.js'],
            'module_tag': 'FINANCE · AI',
            'accent': 'var(--cyan)',
            'accent_glow': 'var(--cyan-glow)',
        },
        {
            'title': 'Portfolio AI Assistant',
            'desc': 'A personalized AI assistant embedded in this portfolio — trained on my professional profile, stack, and cybersecurity domain knowledge.',
            'url': '/',
            'icon': '🛡️',
            'tech': ['Gemini AI', 'Django', 'NLP'],
            'module_tag': 'SECURITY · BOT',
            'accent': 'var(--pink)',
            'accent_glow': 'var(--pink-glow)',
        }
    ]
    return render(request, 'core/projects.html', {'projects': project_list})

@require_POST
def chat_ask(request):
    try:
        data = json.loads(request.body)
        user_msg = data.get('message', '')

        prompt = f"""You are "Vitalii-Bot v1.0", a professional AI assistant for Vitalii Kandabarov's portfolio.

PROFILE:
- Name: Vitalii Kandabarov
- Location: Arlington, Texas, USA
- Education: MSIS Cybersecurity @ Baylor University (2025–2027); BE Software Engineering @ Baranovichi State University (2016–2020)
- Experience: 6+ years — Teacher Assistant at Baylor (2025–present), Software Engineer Intern at Brazos Innovation Partners (2025), Full Stack Developer at Upwork (2022–2025), JazzTeam (2020–2022), Front-end Developer at Likeit (2018–2020)
- Stack: JavaScript, React, TypeScript, Python, Django, C#, HTML/CSS, Git, Docker, REST APIs, Cybersecurity, AI APIs (Gemini, OpenAI)
- Key achievements: Jira dashboard system (−40% tracking issues), React migration (−25% tech debt), WebSocket audio annotation tool (+50% analysis speed), volunteer at refugee center in Germany
- Certifications: English Proficiency Certificate, AWS Cloud Practitioner (in progress)
- Interests: Anime — Kingdom; Books — The Girl with the Dragon Tattoo (Stieg Larsson), Lupin; Detective fiction, bug hunting

Answer concisely and professionally. If asked about interests/hobbies, mention Kingdom anime, The Girl with the Dragon Tattoo, Lupin.

USER: "{user_msg}"
RESPONSE:"""

        client = _get_client()
        response = client.models.generate_content(model='gemini-2.5-flash-lite', contents=prompt)
        return JsonResponse({'answer': response.text.strip()})
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower() or "503" in error_msg:
            return JsonResponse({'answer': "[AI_STANDBY_MODE] :: Tokens exhausted. Vitalii is an MSIS student at Baylor University specializing in Cybersecurity and Full-Stack Development. 🛡️"})
        return JsonResponse({'answer': "System in legacy mode. Vitalii is a developer specializing in React, Python, and Cybersecurity. 🤖"})
