from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Vote, Voter, Election


def create_vote(election, selected_candidates, voter):
    """
    Creates a vote for the specified election with the selected candidates.

    Parameters
    ----------
    election : Election
        The election for which the vote is being cast.
    selected_candidates : QuerySet
        QuerySet containing the selected Candidate objects for the vote.
    voter : Voter
        The voter casting the vote.

    Returns
    -------
    Vote
        The created Vote object.

    Raises
    ------
    ValidationError
        If the created vote fails validation.

    Notes
    -----
    This function creates a new Vote object for the specified election and sets the chosen candidates
    based on the provided selected_candidates queryset. It then validates the created vote, and if
    validation fails, the vote is deleted and a ValidationError is raised. Finally, the function marks
    the voter as having voted and returns the created vote object.
    """
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
    """
    Checks if the specified user is a voter in the given election.

    Parameters
    ----------
    election : Election
        The election to check for the user's eligibility to vote.
    user : User
        The user to check for eligibility.

    Returns
    -------
    QuerySet
        QuerySet of Voter objects matching the given election and user.

    Notes
    -----
    This function checks if the specified user is registered as a voter for the specified election.
    It returns a QuerySet containing the matching Voter objects.
    """
    return Voter.objects.filter(election=election, user=user)


def create_voter(election, user):
    """
    Creates a new voter for the specified election and user.

    Parameters
    ----------
    election : Election
        The election for which the user is signing up.
    user : User
        The user signing up for the election.

    Returns
    -------
    Voter
        The created Voter object.

    Raises
    ------
    ValidationError
        If the user is already signed up for the election.

    Notes
    -----
    This function attempts to create a new Voter object for the specified election and user.
    If the user is already signed up for the election, it raises a ValidationError.
    """
    if is_voter(election, user):
        raise ValidationError(f"You have already signed up for {election.title}")

    try:
        voter = Voter.objects.create(election=election, user=user)
        voter.full_clean()
        return voter
    except ValidationError as e:
        raise e
