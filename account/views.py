from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib import messages
from django.conf import settings
import urllib.request
import json
import urllib.parse

from account.forms import CustomUserCreationForm
from .utils import verify_recaptcha


class RegisterView(FormView):
    """
    View to handle user registration.

    Attributes
    ----------
    template_name : str
       The path to the template used to render this view.
    form_class : Form
       The form class used for user registration.
    redirect_authenticated_user : bool
       Whether to redirect authenticated users.
    success_url : str
       The URL to redirect to upon successful form submission.

    """
    template_name = 'account/register.html'
    form_class = CustomUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('election:homepage')

    def form_valid(self, form):
        """
        Handles the form validation and user registration.

        Parameters
        ----------
        form : Form
           The validated form instance.

        Returns
        -------
        HttpResponse
           The HTTP response with the result of the form processing.
        """
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    def get(self, *args, **kwargs):
        """
        Handles GET requests to the view.

        Parameters
        ----------
        *args : list
           Additional positional arguments.
        **kwargs : dict
           Additional keyword arguments.

        Returns
        -------
        HttpResponse
           The HTTP response with the rendered template or a redirect.
        """
        if self.request.user.is_authenticated:
            return redirect('election:homepage')
        return super(RegisterView, self).get(*args, **kwargs)


def logout_view(request):
    """
    Log out the user and redirect to the homepage.

    Parameters
    ----------
    request : HttpRequest
       The HTTP request object.

    Returns
    -------
    HttpResponseRedirect
       Redirects to the homepage after logging out the user.
    """
    logout(request)
    return redirect('election:homepage')


def login_user(request):
    """
    Authenticate and log in the user, with reCAPTCHA verification.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponseRedirect or HttpResponse
        Redirects to the homepage if the user is authenticated or the login is successful.
        Redirects to the login page with an error message if authentication fails.
        Renders the login template with the reCAPTCHA public key if the request method is not POST.
    """
    if request.user.is_authenticated:
        return redirect('election:homepage')
    elif request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        recaptcha_response = request.POST.get('g-recaptcha-response')

        if recaptcha_response:
            if verify_recaptcha(recaptcha_response):
                user = authenticate(request, username=username, password=password)
                if user is not None:
                    login(request, user)
                    return redirect('election:homepage')
                else:
                    messages.error(request, "Invalid username or password. Please try again.")
                    return redirect('account:login')
            else:
                messages.error(request, "Please complete the reCAPTCHA.")
                return redirect('account:login')
        else:
            messages.error(request, "Please complete the reCAPTCHA.")
            return redirect('account:login')

    return render(request, 'account/login.html', {'captcha_public_key': settings.CAPTCHA_PUBLIC_KEY})


@login_required
def profile_view(request):
    """
    Display the user's profile page.

    Parameters
    ----------
    request : HttpRequest
        The HTTP request object.

    Returns
    -------
    HttpResponse
        Renders the profile page with the user's information.
    """
    user = request.user
    return render(request, 'account/profile.html', {'user': user})
