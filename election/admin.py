from django.contrib import admin

from .models import Election, Candidate, Party, Vote, Voter, SentEmail


class CandidateInLine(admin.TabularInline):
    """
    Inline admin descriptor for Candidate model.

    Attributes
    ----------
    model : Model
       The model that this inline admin relates to.
    extra : int
       The number of extra forms to display in the admin interface.
    """
    model = Candidate
    extra = 3


class ElectionAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Election model.

    Attributes
    ----------
    fieldsets : list
        The fieldsets for grouping fields in the admin form.
    inlines : list
        The inline admin classes related to this admin class.
    list_display : list
        The fields to display in the list view of the admin interface.
    """
    fieldsets = [
        (None, {"fields": ["title", "description", "image", "max_candidates_choice"]}),
        ("Date information", {"fields": ["start_date", "end_date"]}),
    ]
    inlines = [CandidateInLine]
    list_display = ["title", "start_date", "end_date"]


class VoterAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Voter model.

    Attributes
    ----------
    list_display : list
        The fields to display in the list view of the admin interface.
    """
    list_display = ["election", "user", "has_voted"]


class CandidateAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Candidate model.

    Attributes
    ----------
    list_display : list
       The fields to display in the list view of the admin interface.
    fieldsets : list
       The fieldsets for grouping fields in the admin form.
    """
    list_display = ["name", "election", "party"]
    fieldsets = [
        (None, {"fields": ["name", "party", "picture"]}),
        ("Candidate's election", {"fields": ["election"]})
    ]

class SentEmailAdmin(admin.ModelAdmin):
    """
    Admin configuration for the SentEmail model.

    Attributes
    ----------
    readonly_fields : list
       The fields that are read-only in the admin form.
    list_display : list
       The fields to display in the list view of the admin interface.
    """
    readonly_fields = ["timestamp"]
    list_display = ["subject", "recipient", "timestamp"]


admin.site.register(Election, ElectionAdmin)
admin.site.register(Candidate, CandidateAdmin)
admin.site.register(Party)
admin.site.register(Vote)
admin.site.register(Voter, VoterAdmin)
admin.site.register(SentEmail, SentEmailAdmin)

