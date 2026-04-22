from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='sentiment_dashboard'),
    path('analyze/', views.analyze, name='sentiment_analyze'),
    path('result/<int:pk>/', views.result_detail, name='sentiment_result'),
]
