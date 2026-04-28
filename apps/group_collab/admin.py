from django.contrib import admin
from .models import StudyGroup, Member, Vote, Presentation, PresentationPart

@admin.register(StudyGroup)
class StudyGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'max_members', 'voting_open', 'created_at')
    readonly_fields = ('code',)

admin.site.register(Member)
admin.site.register(Vote)
admin.site.register(Presentation)
admin.site.register(PresentationPart)
