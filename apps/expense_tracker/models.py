from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import datetime


class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    total_monthly_limit = models.DecimalField(max_digits=10, decimal_places=2, default=1500.00)
    current_month = models.DateField(default=datetime.date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'current_month')

    def __str__(self):
        return f"{self.user.username} — {self.current_month.strftime('%B %Y')}"

    def get_total_spent(self):
        start = self.current_month.replace(day=1)
        end = (start + datetime.timedelta(days=32)).replace(day=1)
        return self.user.expenses.filter(date__date__gte=start, date__date__lt=end).aggregate(
            total=models.Sum('amount'))['total'] or 0

    def get_remaining(self):
        return self.total_monthly_limit - self.get_total_spent()

    def get_percentage(self):
        if self.total_monthly_limit == 0:
            return 0
        return round(float(self.get_total_spent()) / float(self.total_monthly_limit) * 100, 1)


class BudgetCategory(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    limit = models.DecimalField(max_digits=10, decimal_places=2)
    icon = models.CharField(max_length=10, default='💰')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.icon} {self.name}"

    def get_spent(self):
        start = self.budget.current_month.replace(day=1)
        end = (start + datetime.timedelta(days=32)).replace(day=1)
        return self.budget.user.expenses.filter(
            date__date__gte=start,
            date__date__lt=end,
            category__iexact=self.name
        ).aggregate(total=models.Sum('amount'))['total'] or 0

    def get_percentage(self):
        if self.limit == 0:
            return 0
        return round(float(self.get_spent()) / float(self.limit) * 100, 1)


class Expense(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses')
    original_text = models.TextField()
    category = models.CharField(max_length=100, default='Прочее')
    subcategory = models.CharField(max_length=100, blank=True, default='')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_necessary = models.BooleanField(default=True)
    ai_comment = models.TextField(blank=True, default='')
    date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.category}: ${self.amount} — {self.date.strftime('%d.%m.%Y')}"


class DailyAdvice(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_advice')
    advice_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Совет для {self.user.username} от {self.created_at.strftime('%d.%m.%Y')}"
