from django.core.exceptions import ValidationError

from .models import Vote, Voter


def create_vote(election, selected_candidates, voter):
    vote = Vote.objects.create(election=election)
    vote.chosen_candidates.set(selected_candidates)

    try:
        vote.full_clean()
    except ValidationError as e:
        vote.delete()
        raise ValidationError('Vote creation failed') from e

    vote.save()

    voter.has_voted = True
    voter.save()
    return vote


def create_voter(election, user):
    if Voter.objects.filter(election=election, user=user).exists():
        raise ValidationError(f"You have already signed up for {election.title}")

    try:
        voter = Voter.objects.create(election=election, user=user)
        voter.full_clean()
        return voter
    except ValidationError as e:
        raise e
