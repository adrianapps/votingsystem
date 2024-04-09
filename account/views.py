from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView

from account.forms import CustomUserCreationForm


class CustomLoginView(LoginView):
    template_name = 'account/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('election:election-list')


class RegisterView(FormView):
    template_name = 'account/register.html'
    form_class = CustomUserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('election:election-list')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterView, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('election:election-list')
        return super(RegisterView, self).get(*args, **kwargs)


def logout_view(request):
    logout(request)
    return redirect('election:election-list')
