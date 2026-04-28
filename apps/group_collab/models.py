import uuid
from django.db import models

def _gen_code():
    return uuid.uuid4().hex[:8].upper()

class StudyGroup(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=8, unique=True, default=_gen_code)
    max_members = models.PositiveIntegerField(default=4)
    voting_open = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} [{self.code}]"

class Member(models.Model):
    ROLES = [
        ('member',     'Member'),
        ('leader',     'Leader'),
        ('designer',   'Designer'),
        ('researcher', 'Researcher'),
        ('speaker',    'Speaker'),
        ('editor',     'Editor'),
    ]
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='members')
    nickname = models.CharField(max_length=50)
    session_key = models.CharField(max_length=100)
    is_leader = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'session_key')

    def __str__(self):
        return f"{self.nickname} @ {self.group.name}"

class Vote(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='votes')
    voter_hash = models.CharField(max_length=64)
    candidate = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='votes_received')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'voter_hash')

class Presentation(models.Model):
    group = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='presentations')
    topic = models.CharField(max_length=300, blank=True)
    full_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.topic or 'Untitled'} — {self.group.name}"

class PresentationPart(models.Model):
    presentation = models.ForeignKey(Presentation, on_delete=models.CASCADE, related_name='parts')
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, blank=True, related_name='parts')
    part_number = models.PositiveIntegerField()
    text = models.TextField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['part_number']
