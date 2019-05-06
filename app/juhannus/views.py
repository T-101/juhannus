import re
from django.shortcuts import get_object_or_404
from django.views import generic

from juhannus.models import Event, Participant
from juhannus.forms import SubmitForm


class EventView(generic.FormView):
    template_name = 'juhannus/index.html'
    form_class = SubmitForm

    def get_success_url(self):
        return self.request.get_full_path()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["events"] = list(Event.objects.order_by("year").values("year"))

        sort_order = self.request.GET.get("sort") or "name"
        sort_order = sort_order if sort_order in ['name', '-name', 'vote', '-vote'] else "name"
        ctx["ascending"] = not bool(re.search("^-", sort_order))

        if not self.kwargs.get("year"):
            ctx['event'] = Event.objects.order_by("year").last()
        else:
            ctx['event'] = get_object_or_404(Event, year=self.kwargs.get("year"))
        ctx["participants"] = ctx["event"].participants.order_by(sort_order)
        return ctx

    def form_valid(self, form):
        print("FORM VALID", form.data.get("action"))
        action = form.data.get("action")
        if action == "modify":
            instance = get_object_or_404(Participant, pk=form.data.get("pk"))
            vote = SubmitForm(self.request.POST, instance=instance)
            vote.save()
        if action == "delete":
            instance = get_object_or_404(Participant, pk=form.data.get("pk"))
            instance.delete()
        if action == "save":
            vote = form.save(commit=False)
            vote.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print("FORM INVALID")
        return super().form_invalid(form)
