from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404
from django.shortcuts import reverse, get_object_or_404, redirect
from django.db import models
from django.utils import timezone

from PIL import Image


class Election(models.Model):
    DEFAULT_IMAGE = 'pictures/default_election.jpg'

    title = models.CharField(max_length=30)
    description = models.TextField(max_length=500, blank=True)
    image = models.ImageField(default=DEFAULT_IMAGE, upload_to='pictures/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    max_candidates_choice = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.image:
            self.image = self.DEFAULT_IMAGE
        super(Election, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('election:election-detail', kwargs={'pk': self.pk})

    def get_result_url(self):
        return reverse('election:election-result', kwargs={'pk': self.pk})


class Party(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(max_length=500, blank=True)
    creation_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Candidate(models.Model):
    DEFAULT_PICTURE = 'pictures/default_pic.jpg'

    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    name = models.CharField(max_length=20)
    picture = models.ImageField(default=DEFAULT_PICTURE, upload_to='pictures/', blank=True, null=True)
    party = models.ForeignKey(Party, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('election:candidate-detail', kwargs={'pk': self.pk})

    def get_update_url(self):
        return reverse('election:candidate-update', kwargs={'pk': self.pk})

    def get_delete_url(self):
        return reverse('election:candidate-delete', kwargs={'pk': self.pk})

    def save(self, *args, **kwargs):
        if not self.picture:
            self.picture = self.DEFAULT_PICTURE

        super(Candidate, self).save(*args, **kwargs)

        picture = Image.open(self.picture.path)
        if picture.height > 300 or picture.width > 300:
            output_size = (300, 300)
            picture.thumbnail(output_size)
            picture.save(self.picture.path)

    def vote_count(self):
        return self.votes.count()


class Voter(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    election = models.ForeignKey(Election, on_delete=models.CASCADE)
    has_voted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} can vote in {self.election}"

    def clean(self):
        if timezone.now() > self.election.start_date:
            raise ValidationError(f"You can't sign up for {self.election.title}, the election has already started")


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
