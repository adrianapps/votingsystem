class CandidateListMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.object
        candidates = election.candidate_set.all()
        context['candidates'] = candidates

        return context
