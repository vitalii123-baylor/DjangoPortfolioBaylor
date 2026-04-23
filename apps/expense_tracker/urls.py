from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='expense_dashboard'),
    path('add/', views.add_expense, name='add_expense'),
    path('advice/', views.get_advice, name='get_advice'),
    path('delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('seed/', views.seed_demo_data, name='seed_expenses'),
    path('clear/', views.clear_data, name='clear_expenses'),
    path('update-budget/', views.update_budget_limit, name='update_budget'),
    path('upload-receipt/', views.upload_receipt, name='upload_receipt'),
]
