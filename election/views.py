import os
import io
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import FileResponse, Http404

from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from votingsystem.settings import EMAIL_HOST_USER
from .models import Election, Candidate, Voter
from .services import create_vote, create_voter, is_voter
from .mixins import CandidateListMixin, StaffMemberRequiredMixin
from .utils import generate_chart
from .forms import ContactForm


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

    def get(self, request, *args, **kwargs):
        election = self.get_object()
        if election.has_finished():
            return redirect(election.get_result_url())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.object
        context['is_voter'] = is_voter(election, self.request.user)
        return context


class ElectionResult(LoginRequiredMixin, CandidateListMixin, DetailView):
    model = Election
    context_object_name = 'election'
    template_name = 'election/election_result.html'

    def get(self, request, *args, **kwargs):
        election = self.get_object()
        if not election.has_finished():
            messages.error(request, f"You can't see the results of {election.title}, it hasn't finished yet")
            return redirect('election:election-list')
        return super().get(request, *args, **kwargs)


class ElectionCreate(StaffMemberRequiredMixin, CreateView):
    model = Election
    fields = '__all__'


class ElectionUpdate(StaffMemberRequiredMixin, UpdateView):
    model = Election
    context_object_name = 'election'
    fields = '__all__'


class ElectionDelete(StaffMemberRequiredMixin, DeleteView):
    model = Election
    success_url = reverse_lazy('election:election-list')


@login_required
def generate_pdf(request, pk):
    election = get_object_or_404(Election, pk=pk)
    if not election.has_finished():
        messages.error(request, f"You can't see the results of {election.title}, it hasn't finished yet")
        return redirect('election:election-list')

    candidates = election.candidate_set.all()

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


def contact_view(request):
    return render(request, 'election/contact.html')


def signup_for_election(request, pk):
    election = get_object_or_404(Election, pk=pk)
    try:
        create_voter(election, request.user)
        messages.success(request, f"You have successfully signed up for {election.title}")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect('election:election-list')


@login_required
def vote(request, pk):
    user = request.user
    try:
        election = get_object_or_404(Election, pk=pk)
        voter = get_object_or_404(Voter, user=user, election=election)
    except Http404:
        messages.error(request, 'You are not a voter, or election does not exist')
        return redirect('election:election-list')

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

    email = EmailMessage(
        subject=user.username,
        body=f"Thank you for voting in {election.title}",
        from_email=EMAIL_HOST_USER,
        to=[user.email],
        reply_to=[EMAIL_HOST_USER],
    )
    email.send()

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


class Contact(FormView):
    template_name = 'election/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('election:election-list')

    def form_valid(self, form):
        name = form.cleaned_data['name']
        email_from = form.cleaned_data['email']
        content = form.cleaned_data['content']

        email = EmailMessage(
            subject=name,
            body=content,
            from_email=email_from,
            to=[EMAIL_HOST_USER],
            reply_to=[email_from],
        )
        email.send()
        messages.success(self.request, f"{name}, your email has been sent successfully")
        return super().form_valid(form)


def about_us_view(request):
    return render(request, 'election/about_us.html')


def homepage_view(request):
    return render(request, 'election/homepage.html')


def search(request):
    query = request.GET.get('q', None)
    elections = Election.objects.all()
    if query is not None:
        elections = elections.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
    context = {
        'elections': elections,
        'query': query
    }
    return render(request, 'election/search.html', context)


# Widok dla zakladki profil user
@login_required
def profile_view(request):
    # Pobierz aktualnie zalogowanego użytkownika
    user = request.user

    # Przekazujemy użytkownika do szablonu HTML
    return render(request, 'election/profile.html', {'user': user})
