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
