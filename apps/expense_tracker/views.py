import json
import datetime
from decimal import Decimal
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Budget, BudgetCategory, Expense, DailyAdvice
from .claude_service import categorize_expense, generate_daily_advice

ICON_MAP = {
    'coffee': '☕', 'car': '🚗', 'film': '🎬', 'shopping-bag': '🛍️',
    'heart': '💊', 'food': '🍔', 'transport': '🚗', 'entertainment': '🎬',
    'shopping': '🛍️', 'health': '💊', 'home': '🏠', 'music': '🎵',
    'book': '📚', 'gift': '🎁', 'plane': '✈️', 'phone': '📱',
    'zap': '⚡', 'dollar-sign': '💵', 'credit-card': '💳',
}

def resolve_icon(icon: str) -> str:
    if icon in ICON_MAP:
        return ICON_MAP[icon]
    if len(icon) <= 4:
        return icon
    return '💰'

def get_demo_user():
    user = User.objects.filter(username='demo').first()
    if not user:
        user = User.objects.create_user(username='demo', password='password_not_needed_for_demo')
    return user

def get_dashboard_data(user):
    budget = Budget.objects.filter(user=user).order_by('-current_month').first()
    if not budget:
        month_start = datetime.date.today().replace(day=1)
        budget = Budget.objects.create(user=user, current_month=month_start, total_monthly_limit=Decimal('2500.00'))
        # Create default categories
        default_cats = [
            ('Food & Drinks', '☕', 500),
            ('Transport', '🚗', 300),
            ('Entertainment', '🎬', 200),
            ('Shopping', '🛍️', 400),
            ('Health', '💊', 150),
        ]
        for name, icon, limit in default_cats:
            BudgetCategory.objects.create(budget=budget, name=name, icon=icon, limit=Decimal(str(limit)))
    
    today = datetime.date.today()
    # Берем расходы за последние 30 дней для адекватного графика
    start_date = today - datetime.timedelta(days=30)
    expenses = Expense.objects.filter(user=user, date__date__gte=start_date).order_by('-date')
    
    categories = []
    for cat in budget.categories.all():
        spent = cat.get_spent()
        categories.append({
            'name': cat.name, 'icon': resolve_icon(cat.icon), 'spent': float(spent),
            'limit': float(cat.limit), 'percentage': cat.get_percentage()
        })
    
    # Группировка по дням для графика
    daily_map = {}
    # Генерируем последние 7 дней, чтобы график не был пустым
    for i in range(7):
        d = (today - datetime.timedelta(days=i)).strftime('%b %d')
        daily_map[d] = 0

    for exp in expenses:
        d_str = exp.date.strftime('%b %d')
        if d_str in daily_map:
            daily_map[d_str] += float(exp.amount)
    
    # Сортируем даты хронологически для Chart.js
    sorted_days = sorted(daily_map.keys(), key=lambda x: datetime.datetime.strptime(x, '%b %d'))
    daily_values = [daily_map[day] for day in sorted_days]

    return {
        'total_spent': float(budget.get_total_spent()),
        'total_limit': float(budget.total_monthly_limit),
        'total_percentage': float(budget.get_percentage()),
        'total_remaining': float(budget.get_remaining()),
        'categories': categories,
        'daily_labels': sorted_days,
        'daily_values': daily_values,
        'expenses': [{'id': e.id, 'text': e.original_text, 'amount': float(e.amount), 'cat': e.category, 'date': e.date.strftime('%b %d')} for e in expenses[:10]]
    }

def dashboard(request):
    user = get_demo_user()
    data = get_dashboard_data(user)
    today_advice = DailyAdvice.objects.filter(user=user, created_at__date=datetime.date.today()).first()
    return render(request, 'expense_tracker/dashboard.html', {**data, 'today_advice': today_advice})

@require_POST
def add_expense(request):
    try:
        user = get_demo_user()
        data = json.loads(request.body)
        result = categorize_expense(data.get('text', ''))
        Expense.objects.create(
            user=user, original_text=data.get('text'), category=result.get('category', 'Other'),
            amount=Decimal(str(result.get('amount', 0))), is_necessary=True, ai_comment=result.get('advice')
        )
        return JsonResponse(get_dashboard_data(user))
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_POST
def seed_demo_data(request):
    user = get_demo_user()
    today = datetime.date.today()
    
    # Создаем данные, распределенные по времени
    samples = [
        ('Starbucks', 'Food & Drinks', 15, 0),
        ('Uber', 'Transport', 45, 1),
        ('Groceries', 'Food & Drinks', 120, 2),
        ('Cinema', 'Entertainment', 35, 3),
        ('Amazon', 'Shopping', 250, 4),
        ('Restaurant', 'Food & Drinks', 80, 5),
        ('Gym', 'Health', 60, 6),
    ]
    
    for text, cat, amt, days_ago in samples:
        date = datetime.datetime.now() - datetime.timedelta(days=days_ago)
        Expense.objects.create(
            user=user, original_text=text, category=cat, 
            amount=Decimal(str(amt)), is_necessary=True, date=date
        )
    return JsonResponse(get_dashboard_data(user))

@require_POST
def clear_data(request):
    user = get_demo_user()
    Expense.objects.filter(user=user).delete()
    return JsonResponse(get_dashboard_data(user))

@require_POST
def update_budget_limit(request):
    user = get_demo_user()
    data = json.loads(request.body)
    budget = Budget.objects.filter(user=user).first()
    budget.total_monthly_limit = Decimal(str(data.get('limit', 2500)))
    budget.save()
    return JsonResponse(get_dashboard_data(user))

def get_advice(request):
    user = get_demo_user()
    advice = generate_daily_advice("Analysis of spending patterns.")
    return JsonResponse({'advice': advice})

def delete_expense(request, pk):
    user = get_demo_user()
    get_object_or_404(Expense, pk=pk, user=user).delete()
    return JsonResponse(get_dashboard_data(user))
