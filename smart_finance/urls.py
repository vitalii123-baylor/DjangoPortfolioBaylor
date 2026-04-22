from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('api/expenses/', include('apps.expense_tracker.urls')),
    path('api/sentiment/', include('apps.sentiment_analyzer.urls')),
]
