from django.contrib import admin

from .models import Election, Candidate, Party, Vote, Voter

admin.site.register(Election)
admin.site.register(Candidate)
admin.site.register(Party)
admin.site.register(Vote)
admin.site.register(Voter)
