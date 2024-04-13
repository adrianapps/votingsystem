from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin

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


class ElectionDetail(LoginRequiredMixin, DetailView):
    model = Election
    context_object_name = 'election'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.object
        candidates = election.candidate_set.all()
        context['candidates'] = candidates

        return context


class ElectionResult(LoginRequiredMixin, DetailView):
    model = Election
    context_object_name = 'election'
    template_name = 'election/election_result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.object
        candidates = election.candidate_set.all()
        context['candidates'] = candidates

        return context


@login_required
def vote(request, pk):
    election = get_object_or_404(Election, pk=pk)
    voter = get_object_or_404(Voter, user=request.user, election=election)

    if voter.has_voted:
        raise Http404('You have already voted')

    selected_candidates_ids = request.POST.getlist('candidate')

    if not selected_candidates_ids:
        messages.error(request, 'No candidates selected')
        return redirect(election.get_absolute_url())

    selected_candidates = Candidate.objects.filter(pk__in=selected_candidates_ids)

    if len(selected_candidates_ids) != len(selected_candidates):
        messages.error(request, 'Candidate does not exist')
        return redirect(election.get_absolute_url())

    create_vote(election, selected_candidates, voter)

    messages.success(request, 'Your vote has been cast successfully')
    return redirect(election.get_result_url())


def contact_view(request):
    return render(request, 'election/contact.html')


def about_us_view(request):
    return render(request, 'election/about_us.html')


# Widok dla zakladki profil user
@login_required
def profile_view(request):
    # Pobierz aktualnie zalogowanego użytkownika
    user = request.user

    # Przekazujemy użytkownika do szablonu HTML
    return render(request, 'election/profile.html', {'user': user})
