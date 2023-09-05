import re

from django.db.models.functions import Lower
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views import generic
from django.utils import timezone

from juhannus.models import Event, Participant, get_midsummer_saturday
from juhannus.forms import SubmitForm


class EventView(generic.FormView):
    template_name = 'juhannus/index.html'
    form_class = SubmitForm

    def __init__(self):
        super().__init__()
        self.events = Event.objects.select_related("body", "header").order_by("year")

    def dispatch(self, request, *args, **kwargs):
        if not self.events:
            return HttpResponse("No events in db")

        # use .localtime() when comparing to pytz-created datetime object
        year = timezone.localtime().year
        if timezone.localtime().strftime("%V") == get_midsummer_saturday(year).strftime("%V"):
            # Only hit db when the week is correct
            if not Event.objects.filter(year=year):
                previous = Event.objects.order_by("year").last()
                Event.objects.create(year=year, header=previous.header, body=previous.body)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.request.get_full_path()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["events"] = self.events

        sort_order = "vote" if self.request.GET.get("vote") else "name"

        if not self.kwargs.get("year"):
            ctx['event'] = self.events.order_by("year").last()
        else:
            try:
                ctx["event"] = self.events.get(year=self.kwargs.get("year"))
            except Event.DoesNotExist:
                raise Http404

        ctx["participants"] = ctx["event"].participants.order_by(
            sort_order if sort_order == "vote" else Lower(sort_order))

        ctx["ascending"] = False if self.request.GET.get(sort_order, "").lower() == "desc" else True

        if not ctx["ascending"]:
            ctx["participants"] = ctx["participants"].reverse()
        return ctx

    def form_valid(self, form):
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
