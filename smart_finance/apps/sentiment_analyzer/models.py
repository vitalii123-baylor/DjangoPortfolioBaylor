from django.db import models
from django.contrib.auth.models import User


class SentimentSearch(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sentiment_searches')
    topic = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} → {self.topic}"


class SentimentResult(models.Model):
    search = models.OneToOneField(SentimentSearch, on_delete=models.CASCADE, related_name='result')
    positive_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    negative_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    neutral_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total_posts_analyzed = models.IntegerField(default=0)
    positive_count = models.IntegerField(default=0)
    negative_count = models.IntegerField(default=0)
    neutral_count = models.IntegerField(default=0)
    top_keywords = models.JSONField(default=list)
    ai_analysis = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result for '{self.search.topic}'"


class SocialPost(models.Model):
    SENTIMENT_CHOICES = [
        ('positive', 'Позитивный'),
        ('negative', 'Негативный'),
        ('neutral', 'Нейтральный'),
    ]
    result = models.ForeignKey(SentimentResult, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    source = models.CharField(max_length=50, default='demo')
    sentiment = models.CharField(max_length=20, choices=SENTIMENT_CHOICES)
    confidence = models.DecimalField(max_digits=4, decimal_places=3, default=0.5)
    author = models.CharField(max_length=100, blank=True, default='')
    post_url = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-confidence']

    def __str__(self):
        return f"[{self.sentiment}] {self.content[:50]}"
