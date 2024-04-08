from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.shortcuts import render

from .models import Election, Candidate, Vote, Voter
from .services import create_vote


class ElectionList(ListView):
    model = Election
    context_object_name = 'elections'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            elections = context['elections']
            has_voted = [election.id for election in elections if Voter.objects.filter(
                user=self.request.user, election=election, has_voted=True)]
            context['has_voted'] = has_voted
        return context


class ElectionDetail(DetailView):
    model = Election
    context_object_name = 'election'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.object
        candidates = election.candidate_set.all()
        context['candidates'] = candidates

        return context


@login_required
def vote(request, pk):
    election = get_object_or_404(Election, pk=pk)

    try:
        voter = get_object_or_404(Voter, user=request.user, election=election)
    except Voter.DoesNotExist:
        raise Http404('You are not a voter')

    if voter.has_voted:
        raise Http404('You have already voted')

    try:
        selected_candidates = election.candidate_set.get(pk=request.POST['candidate'])
    except (KeyError, Candidate.DoesNotExist):
        messages.error(request, 'Invalid candidate selected')
        return redirect(election.get_absolute_url())

    create_vote(election, selected_candidates, voter)

    messages.success(request, 'Your vote has been cast successfully')
    return redirect('election:election-list')

def contact_view(request):
    return render(request, 'contact.html')

def election_view(request):
    return render(request, 'election_list.html')