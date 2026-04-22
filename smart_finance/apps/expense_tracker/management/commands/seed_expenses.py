import random
from datetime import datetime, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.expense_tracker.models import Expense, Budget, BudgetCategory

class Command(BaseCommand):
    help = 'Seeds the database with realistic expense data for 2026'

    def handle(self, *args, **kwargs):
        user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No user found. Create a user first.'))
            return

        # Clear existing data
        Expense.objects.filter(user=user).delete()
        
        # Setup Budget if not exists
        today = datetime.today()
        month_start = today.replace(day=1)
        budget, _ = Budget.objects.get_or_create(
            user=user, 
            current_month=month_start,
            defaults={'total_monthly_limit': Decimal('2500.00')}
        )

        categories = [
            ('Food & Drinks', Decimal('800.00'), '🍔', ['Starbucks', 'Grocery Store', 'Sushi Dinner', 'Burger King']),
            ('Transport', Decimal('300.00'), '🚗', ['Uber ride', 'Gas station', 'Bus pass', 'Tesla Supercharger']),
            ('Entertainment', Decimal('500.00'), '🎮', ['Cinema', 'Steam Store', 'Concert ticket', 'Bowling']),
            ('Subscriptions', Decimal('400.00'), '📱', ['Netflix', 'Spotify', 'ChatGPT Plus', 'Midjourney AI']),
            ('Health', Decimal('300.00'), '💊', ['Pharmacy', 'Gym membership', 'Dentist', 'Vitamins']),
            ('Shopping', Decimal('500.00'), '🛍️', ['Amazon', 'Apple Store', 'Nike', 'H&M']),
        ]

        # Ensure categories exist
        for name, limit, icon, _ in categories:
            BudgetCategory.objects.get_or_create(budget=budget, name=name, defaults={'limit': limit, 'icon': icon})

        # Generate 40-50 expenses for the last 30 days
        for i in range(45):
            days_ago = random.randint(0, 30)
            date = datetime.now() - timedelta(days=days_ago)
            cat_info = random.choice(categories)
            
            name = random.choice(cat_info[3])
            amount = Decimal(str(round(random.uniform(5.0, 150.0), 2)))
            
            Expense.objects.create(
                user=user,
                original_text=f"{name} ${amount}",
                category=cat_info[0],
                amount=amount,
                date=date,
                is_necessary=random.choice([True, True, False]), # More likely to be necessary
                ai_comment="Generated for demo purposes."
            )

        self.stdout.write(self.style.SUCCESS(f'Successfully seeded 45 expenses for {user.username}'))
