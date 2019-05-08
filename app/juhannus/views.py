import re

from django.db.models.functions import Lower
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views import generic

from juhannus.models import Event, Participant
from juhannus.forms import SubmitForm


class EventView(generic.FormView):
    template_name = 'juhannus/index.html'
    form_class = SubmitForm

    def dispatch(self, request, *args, **kwargs):
        if not Event.objects.count():
            return HttpResponse("No event in db")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.get_full_path()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["events"] = list(Event.objects.order_by("year").values("year"))

        sort_order = "vote" if self.request.GET.get("vote") else "name"

        if not self.kwargs.get("year"):
            ctx['event'] = Event.objects.order_by("year").last()
        else:
            ctx['event'] = get_object_or_404(Event, year=self.kwargs.get("year"))

        ctx["participants"] = ctx["event"].participants.order_by(Lower(sort_order))

        ctx["ascending"] = False if self.request.GET.get(sort_order, "").lower() == "desc" else True

        if not ctx["ascending"]:
            ctx["participants"] = ctx["participants"].reverse()
        return ctx

    def form_valid(self, form):
        print("FORM VALID", form.data.get("action"))
        action = form.data.get("action")
        if action == "modify" and self.request.user.is_staff:
            instance = get_object_or_404(Participant, pk=form.data.get("pk"))
            vote = SubmitForm(self.request.POST, instance=instance)
            vote.save()
        if action == "delete" and self.request.user.is_staff:
            instance = get_object_or_404(Participant, pk=form.data.get("pk"))
            instance.delete()
        if action == "save":
            vote = form.save(commit=False)
            if vote.event.is_voting_available() or self.request.user.is_staff:
                vote.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        print("FORM INVALID")
        return super().form_invalid(form)
