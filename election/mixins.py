from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect

from votingsystem.settings import LOGIN_URL


class CandidateListMixin:
    """
    A mixin for Django class-based views to add candidate list to context data.
    """
    def get_context_data(self, **kwargs):
        """
        Add candidate list to the context data.

        Returns:
            dict: The updated context data with candidates added.

        """
        context = super().get_context_data(**kwargs)
        election = self.object
        candidates = election.candidate_set.all()
        context['candidates'] = candidates

        return context


class StaffMemberRequiredMixin(UserPassesTestMixin):
    """
    A mixin to restrict access to views to staff members only.

    Attributes:
        permission_denied_message (str): The message to be displayed when permission is denied.
        redirect_field_name (str): The name of the redirect field.
        login_url (str): The URL to redirect to for login.
    """

    permission_denied_message = 'Unable to add candidates, you are not a staff member'
    redirect_field_name = 'election:election-list'
    login_url = LOGIN_URL

    def test_func(self):
        """
        Check if the user is a staff member.

        Returns:
           bool: True if the user is a staff member, False otherwise.
        """
        return self.request.user.is_staff

    def handle_no_permission(self):
        """
        Handle the case where the user does not have permission to access the view.

        Returns:
            HttpResponseRedirect: Redirects the user to the login page or the election list page.
        """
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)
        else:
            messages.error(self.request, self.get_permission_denied_message())
            return redirect(self.redirect_field_name)
