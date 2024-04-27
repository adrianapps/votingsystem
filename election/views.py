import os
import io

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import FileResponse

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from .models import Election, Candidate, Voter
from .services import create_vote
from .mixins import CandidateListMixin, StaffMemberRequiredMixin
from .utils import generate_chart


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


class ElectionDetail(LoginRequiredMixin, CandidateListMixin, DetailView):
    model = Election
    context_object_name = 'election'


class ElectionResult(LoginRequiredMixin, CandidateListMixin, DetailView):
    model = Election
    context_object_name = 'election'
    template_name = 'election/election_result.html'

    def get(self, request, *args, **kwargs):
        election = self.get_object()
        if not election.voter_set.filter(election=election, user=request.user, has_voted=True).exists():
            messages.error(request, f"Unable to see the results. You are not a voter in {election.title}")
            return redirect('election:election-list')
        return super().get(request, *args, **kwargs)


@login_required
def generate_pdf(request, pk):
    election = get_object_or_404(Election, pk=pk)
    candidates = election.candidate_set.all()

    if not election.voter_set.filter(election=election, user=request.user, has_voted=True).exists():
        messages.error(request, f"Unable to see the results. You are not a voter in {election.title}")
        return redirect('election:election-list')

    candidate_names = []
    candidate_votes = []

    for candidate in candidates:
        candidate_names.append(candidate.name)
        candidate_votes.append(candidate.vote_count())

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter, bottomup=0)
    textob = c.beginText()
    textob.setTextOrigin(inch, inch)
    textob.setFont("Helvetica", 14)

    for name, votes in zip(candidate_names, candidate_votes):
        textob.textLine(f"{name} {votes} votes")
    c.drawText(textob)

    chart = generate_chart(candidate_names, candidate_votes)
    c.scale(1, -1)
    c.drawImage(chart, 100, -100, width=400, height=-300)

    c.showPage()
    c.save()
    os.remove(chart)
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='result.pdf')


@login_required
def vote(request, pk):
    election = get_object_or_404(Election, pk=pk)
    voter = get_object_or_404(Voter, user=request.user, election=election)

    if voter.has_voted:
        messages.error(request, f'You have already voted in {election}')
        return redirect('election:election-list')
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


class CandidateDetail(DetailView):
    model = Candidate
    context_object_name = 'candidate'


class CandidateCreate(StaffMemberRequiredMixin, CreateView):
    model = Candidate
    fields = '__all__'


class CandidateUpdate(StaffMemberRequiredMixin, UpdateView):
    model = Candidate
    context_object_name = 'candidate'
    fields = '__all__'


class CandidateDelete(StaffMemberRequiredMixin, DeleteView):
    model = Candidate
    success_url = reverse_lazy('election:election-list')


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
