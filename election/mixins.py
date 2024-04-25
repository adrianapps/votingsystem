from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect


class CandidateListMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.object
        candidates = election.candidate_set.all()
        context['candidates'] = candidates

        return context


class StaffMemberRequiredMixin(UserPassesTestMixin):
    permission_denied_message = 'Unable to add candidates, you are not a staff member'
    redirect_field_name = 'election:election-list'
    login_url = 'account:login'

    def test_func(self):
        return self.request.user.is_staff

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect(self.login_url)
        else:
            messages.error(self.request, self.get_permission_denied_message())
            return redirect(self.redirect_field_name)