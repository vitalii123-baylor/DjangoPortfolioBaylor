from django.contrib import admin
from .models import Budget, BudgetCategory, Expense

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_monthly_limit', 'current_month')

@admin.register(BudgetCategory)
class BudgetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'limit', 'budget')

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date', 'is_necessary')
    list_filter = ('category', 'is_necessary')
