from django.contrib import admin
from .models import SentimentSearch, SentimentResult, SocialPost

@admin.register(SentimentSearch)
class SentimentSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'created_at')

@admin.register(SentimentResult)
class SentimentResultAdmin(admin.ModelAdmin):
    list_display = ('search', 'positive_percentage', 'negative_percentage', 'neutral_percentage', 'total_posts_analyzed')

@admin.register(SocialPost)
class SocialPostAdmin(admin.ModelAdmin):
    list_display = ('sentiment', 'confidence', 'source', 'content')
    list_filter = ('sentiment', 'source')
