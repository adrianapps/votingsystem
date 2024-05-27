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
from .models import Election, Candidate, Voter, SentEmail
from .services import create_vote, create_voter, is_voter
from .mixins import CandidateListMixin, StaffMemberRequiredMixin
from .utils import generate_chart
from .forms import ContactForm


class ElectionList(ListView):
    """
       Displays a list of elections.

       Attributes
       ----------
       model : Model
           The model that this view will be displaying.
       context_object_name : str
           The name of the context variable that will contain the list of objects.
       """
    model = Election
    context_object_name = 'elections'

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the template.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            The context data dictionary containing the list of elections and
            an additional key 'has_voted' that includes a list of election IDs
            where the current user has already voted.

        Notes
        -----
        If the user is not authenticated, the 'has_voted' key will not be added
        to the context data.
        """
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['has_voted'] = Voter.objects.filter(
                user=self.request.user, has_voted=True
            ).values_list('election_id', flat=True)
        return context


class ElectionDetail(LoginRequiredMixin, CandidateListMixin, DetailView):
    """
       Displays the details of a specific election.

       Attributes
       ----------
       model : Model
           The model that this view will be displaying.
       context_object_name : str
           The name of the context variable that will contain the object.
       """
    model = Election
    context_object_name = 'election'

    def get(self, request, *args, **kwargs):
        """
        Handle GET requests to display election details.

        Parameters
        ----------
        request : HttpRequest
            The request object used to generate this response.
        *args : tuple
            Additional positional arguments.
        **kwargs : dict
            Additional keyword arguments.

        Returns
        -------
        HttpResponse
            The HTTP response object containing the rendered template.
        HttpResponseRedirect
            Redirects to the election results if the election has finished or
            if the user has already voted.

        Notes
        -----
        If the election has finished, the user is redirected to the results page.
        If the user has already voted, a message is displayed and the user is
        redirected to the election list.
        """
        election = self.get_object()
        if election.has_finished():
            return redirect(election.get_result_url())
        try:
            voter = Voter.objects.get(election=election, user=request.user)
        except Voter.DoesNotExist:
            voter = None
        if voter and voter.has_voted:
            messages.info(request, f"You have already voted in {election.title}")
            return redirect('election:election-list')
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Get the context data for rendering the template.

        Parameters
        ----------
        **kwargs : dict
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            The context data dictionary containing the election details and
            an additional key 'is_voter' indicating if the current user is a voter
            in the election.
        """
        context = super().get_context_data(**kwargs)
        election = self.object
        context['is_voter'] = is_voter(election, self.request.user)
        return context


class ElectionResult(LoginRequiredMixin, CandidateListMixin, DetailView):
    """
    Displays the results of a specific election.

    Attributes
    ----------
    model : Model
        The model that this view will be displaying.
    context_object_name : str
        The name of the context variable that will contain the object.
    template_name : str
        The template to use for rendering this view.
    """
    model = Election
    context_object_name = 'election'
    template_name = 'election/election_result.html'

    def get(self, request, *args, **kwargs):
        """
       Handle GET requests to display election results.

       Parameters
       ----------
       request : HttpRequest
           The request object used to generate this response.
       *args : tuple
           Additional positional arguments.
       **kwargs : dict
           Additional keyword arguments.

       Returns
       -------
       HttpResponse
           The HTTP response object containing the rendered template.
       HttpResponseRedirect
           Redirects to the election list if the election has not finished yet.

       Notes
       -----
       If the election has not finished, a message is displayed and the user is
       redirected to the election list.
       """
        election = self.get_object()
        if not election.has_finished():
            messages.error(request, f"You can't see the results of {election.title}, it hasn't finished yet")
            return redirect('election:election-list')
        return super().get(request, *args, **kwargs)


class ElectionCreate(StaffMemberRequiredMixin, CreateView):
    """
    Allows staff members to create a new election.

    Attributes
    ----------
    model : Model
        The model that this view will be creating.
    fields : str
        Specifies that all fields of the model should be included in the form.
    """
    model = Election
    fields = '__all__'


class ElectionUpdate(StaffMemberRequiredMixin, UpdateView):
    """
    Allows staff members to update an existing election.

    Attributes
    ----------
    model : Model
      The model that this view will be updating.
    context_object_name : str
      The name of the context variable that will contain the object.
    fields : str
      Specifies that all fields of the model should be included in the form.
    """
    model = Election
    context_object_name = 'election'
    fields = '__all__'


class ElectionDelete(StaffMemberRequiredMixin, DeleteView):
    """
    Allows staff members to delete an existing election.

    Attributes
    ----------
    model : Model
       The model that this view will be deleting.
    success_url : str
       The URL to redirect to after the deletion is successful.
    """
    model = Election
    success_url = reverse_lazy('election:election-list')


@login_required
def generate_pdf(request, pk):
    """
    Generates a PDF report of election results.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate this response.
    pk : int
        The primary key of the election for which the PDF report is generated.

    Returns
    -------
    FileResponse
        The HTTP response object containing the generated PDF file.

    Notes
    -----
    This function generates a PDF report summarizing the results of the election
    specified by its primary key (`pk`). If the election has not finished yet,
    an error message is displayed, and the user is redirected to the election list.

    The PDF report includes:
    - Names of candidates along with their vote counts.
    - A chart visualizing the vote distribution among candidates.
    """
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

    chart = generate_chart(candidate_names, candidate_votes)
    c.scale(1, -1)
    c.drawImage(chart, 100, -100, width=400, height=-300)
    c.showPage()
    c.save()
    buf.seek(0)

    return FileResponse(buf, as_attachment=True, filename='result.pdf')


def contact_view(request):
    """
    Displays the contact page.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate this response.

    Returns
    -------
    HttpResponse
        The HTTP response object containing the rendered contact page.
    """
    return render(request, 'election/contact.html')


def signup_for_election(request, pk):
    """
    Signs up the current user to vote in a specific election.

    Parameters
    ----------
    request : HttpRequest
       The request object used to generate this response.
    pk : int
       The primary key of the election to sign up for.

    Returns
    -------
    HttpResponseRedirect
       Redirects to the election list page after signing up.

    Notes
    -----
    This function attempts to sign up the current user to vote in the election
    specified by its primary key (`pk`). If the signup is successful, a success
    message is displayed. If there is a validation error, an error message is
    displayed instead. Regardless of the outcome, the user is redirected to
    the election list page.
    """
    election = get_object_or_404(Election, pk=pk)
    try:
        create_voter(election, request.user)
        messages.success(request, f"You have successfully signed up for {election.title}")
    except ValidationError as e:
        messages.error(request, str(e))
    return redirect('election:election-list')


@login_required
def vote(request, pk):
    """
    Handles the process of casting a vote in an election.

    Parameters
    ----------
    request : HttpRequest
        The request object containing POST data with the selected candidate IDs.
    pk : int
        The primary key of the election in which the vote is cast.

    Returns
    -------
    HttpResponseRedirect
        Redirects to the election list page after voting.

    Notes
    -----
    This function allows an authenticated user to cast their vote in the election
    specified by its primary key (`pk`). It verifies if the user is eligible to
    vote in the election and if they have not already voted. If the user has already
    voted or if no candidates are selected, appropriate error messages are displayed
    and the user is redirected to the election details page. If the selected candidate
    IDs do not match existing candidates or if there is a validation error during the
    vote creation process, error messages are displayed and the user is redirected to
    the election list page. If the vote is successfully cast, a success message is
    displayed and the user is redirected to the election list page.
    """
    election = get_object_or_404(Election, pk=pk)
    try:
        voter = Voter.objects.get(election=election, user=request.user)
    except Voter.DoesNotExist:
        messages.error(request, f"You are not a voter in {election.title}")
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

    try:
        create_vote(election, selected_candidates, voter)
    except ValidationError as e:
        messages.error(request, str(e))
        return redirect('election:election-list')

    messages.success(request, 'Your vote has been cast successfully')
    return redirect('election:election-list')


class CandidateDetail(DetailView):
    """
    Displays the details of a specific candidate.

    Attributes
    ----------
    model : Model
        The model that this view will be displaying.
    context_object_name : str
        The name of the context variable that will contain the object.
    """
    model = Candidate
    context_object_name = 'candidate'


class CandidateCreate(StaffMemberRequiredMixin, CreateView):
    """
    Allows staff members to create a new candidate.

    Attributes
    ----------
    model : Model
        The model that this view will be creating.
    fields : str
        Specifies that all fields of the model should be included in the form.
    """
    model = Candidate
    fields = '__all__'


class CandidateUpdate(StaffMemberRequiredMixin, UpdateView):
    """
    Allows staff members to update an existing candidate.

    Attributes
    ----------
    model : Model
        The model that this view will be updating.
    context_object_name : str
        The name of the context variable that will contain the object.
    fields : str
        Specifies that all fields of the model should be included in the form.
    """
    model = Candidate
    context_object_name = 'candidate'
    fields = '__all__'


class CandidateDelete(StaffMemberRequiredMixin, DeleteView):
    """
    Allows staff members to delete an existing candidate.

    Attributes
    ----------
    model : Model
        The model that this view will be deleting.
    success_url : str
        The URL to redirect to after the deletion is successful.
    """
    model = Candidate
    success_url = reverse_lazy('election:election-list')


class Contact(FormView):
    """
    Handles the contact form submission and sends an email.

    Attributes
    ----------
    template_name : str
        The name of the template to use for rendering this view.
    form_class : Form
        The form class to use for processing the contact form.
    success_url : str
        The URL to redirect to after the form is successfully processed.
    """

    template_name = 'election/contact.html'
    form_class = ContactForm
    success_url = reverse_lazy('election:election-list')

    def form_valid(self, form):
        """
        Sends an email using the form data and creates a record of the sent email.

        Parameters
        ----------
        form : Form
            The validated form containing the contact information.

        Returns
        -------
        HttpResponse
            The HTTP response object after successfully processing the form.

        Notes
        -----
        This method extracts the name, email, and content from the validated form data.
        It then constructs an email message with the extracted information and sends it.
        After sending the email, it creates a record of the sent email in the database.
        Finally, it displays a success message to the user.
        """
        name = form.cleaned_data['name']
        email_from = form.cleaned_data['email']
        content = form.cleaned_data['content']

        email = EmailMessage(
            subject=name,
            body=content,
            from_email=EMAIL_HOST_USER,
            to=[EMAIL_HOST_USER],
            reply_to=[email_from],
        )
        email.send()
        SentEmail.objects.create(
            sender=EMAIL_HOST_USER,
            recipient=EMAIL_HOST_USER,
            subject=name,
            body=content,
            reply_to=email_from,
        )
        messages.success(self.request, f"{name}, your email has been sent successfully")
        return super().form_valid(form)


def about_us_view(request):
    """
    Renders the 'about us' page.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate this response.

    Returns
    -------
    HttpResponse
        The HTTP response object containing the rendered 'about us' page.
    """
    return render(request, 'election/about_us.html')


def homepage_view(request):
    """
    Renders the homepage.

    Parameters
    ----------
    request : HttpRequest
        The request object used to generate this response.

    Returns
    -------
    HttpResponse
        The HTTP response object containing the rendered homepage.
    """
    return render(request, 'election/homepage.html')


def search(request):
    """
    Handles the search functionality for elections.

    Parameters
    ----------
    request : HttpRequest
        The request object containing the search query.

    Returns
    -------
    HttpResponse
        The HTTP response object containing the search results.

    Notes
    -----
    This function retrieves the search query from the request parameters.
    It then queries the Election model to filter elections based on the
    title or description containing the search query. If no query is
    provided, all elections are retrieved. The search results are passed
    to the template along with the original query for rendering.
    """
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
