from django.contrib import admin

from .models import Election, Candidate, Party, Vote, Voter


class CandidateInLine(admin.TabularInline):
    model = Candidate
    extra = 3


class ElectionAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {"fields": ["title", "description", "image", "max_candidates_choice"]}),
        ("Date information", {"fields": ["start_date", "end_date"]}),
    ]
    inlines = [CandidateInLine]
    list_display = ["title", "start_date", "end_date"]


class VoterAdmin(admin.ModelAdmin):
    list_display = ["election", "user", "has_voted"]


class CandidateAdmin(admin.ModelAdmin):
    list_display = ["name", "election", "party"]
    fieldsets = [
        (None, {"fields": ["name", "party", "picture"]}),
        ("Candidate's election", {"fields": ["election"]})
    ]


admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Party)
admin.site.register(Vote)
admin.site.register(Voter, VoterAdmin)
