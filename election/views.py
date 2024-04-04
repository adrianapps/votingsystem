from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages

from .models import Election, Candidate, Vote, Voter


class ElectionList(ListView):
    model = Election
    context_object_name = 'elections'


class ElectionDetail(DetailView):
    model = Election
    context_object_name = 'election'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.object
        candidates = election.candidate_set.all()
        context['candidates'] = candidates
        return context


def vote(request, pk):
    election = get_object_or_404(Election, pk=pk)
    voter = get_object_or_404(Voter, election=election, user=request.user)

    if voter.has_voted:
        messages.error(request, 'You have already voted in this election')
        return redirect('election:election-list')

    try:
        selected_candidate = election.candidate_set.get(pk=request.POST['candidate'])
    except (KeyError, Candidate.DoesNotExist):
        messages.error(request, 'Invalid candidate selected')
        return redirect('election:election-list')

    choice = Vote.objects.create(election=election)
    choice.chosen_candidates.set([selected_candidate])
    voter.has_voted = True
    voter.save()

    messages.success(request, 'Your vote has been cast successfully')
    return redirect('election:election-list')
