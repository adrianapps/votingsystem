from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Vote, Voter, Election


def create_vote(election, selected_candidates, voter):
    vote = Vote.objects.create(election=election)
    vote.chosen_candidates.set(selected_candidates)

    try:
        vote.full_clean()
    except ValidationError as e:
        vote.delete()
        raise e

    vote.save()

    voter.has_voted = True
    voter.save()
    return vote


def is_voter(election, user):
    return Voter.objects.filter(election=election, user=user)


def create_voter(election, user):
    if is_voter(election, user):
        raise ValidationError(f"You have already signed up for {election.title}")

    try:
        voter = Voter.objects.create(election=election, user=user)
        voter.full_clean()
        return voter
    except ValidationError as e:
        raise e


def get_active_elections():
    now = timezone.now()
    return Election.objects.filter(start_date__lte=now, end_date__gt=now)


def get_finished_elections():
    now = timezone.now()
    return Election.objects.filter(end_date__lte=now)
