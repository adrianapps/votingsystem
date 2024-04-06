from .models import Vote, Voter


def create_vote(election, selected_candidates, voter):
    vote = Vote.objects.create(election=election)
    vote.chosen_candidates.set([selected_candidates])
    voter.has_voted = True

    voter.full_clean()
    voter.save()
    return vote
