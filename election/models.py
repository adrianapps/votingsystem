from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import reverse, get_object_or_404, redirect
from django.db import models


class Election(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_candidates_choice = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def candidate_vote_count(self, candidate):
        return self.vote_set.filter(chosen_candidates=candidate).count()

    def get_absolute_url(self):
        return reverse('election:election-detail', kwargs={'pk': self.pk})


class Party(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Voter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} can vote in {self.election}"


class Vote(models.Model):
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    chosen_candidates = models.ManyToManyField(Candidate, related_name='votes')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        candidates_str = ", ".join(candidate.name for candidate in self.chosen_candidates.all())
        return f"{candidates_str} in {self.election}"

    def chosen_candidate_count(self):
        return self.chosen_candidates.count()

    def clean(self):
        if self.election.max_candidates_choice < self.chosen_candidate_count():
            raise ValidationError(f"You can only choose up to {self.election.max_candidates_choice} candidates")
        elif self.timestamp >= self.election.end_date:
            raise ValidationError(f"The {self.election.title} has already ended")
