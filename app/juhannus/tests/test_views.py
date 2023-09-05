import datetime
from unittest import mock

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from juhannus.models import Event, Participant, get_midsummer_saturday
from juhannus.forms import SubmitForm


class ViewsTests(TestCase):
    fixtures = ['test_juhannus_events.json', 'test_juhannus_users.json']

    def test_empty_db(self):
        endpoint = reverse("juhannus:event-latest")
        self.assertEqual(endpoint, "/")
        with mock.patch('juhannus.models.Event', new=Event.objects.all().delete()):
            response = self.client.get(endpoint)
            self.assertEqual(response.content, b"No events in db")
            self.assertEqual(response.status_code, 200)

    def test_new_event_creation_prior_midsummer_week(self):
        week_before_midsummer = get_midsummer_saturday(2019) - datetime.timedelta(days=7)
        event_count = Event.objects.count()
        with mock.patch('juhannus.models.timezone.now', return_value=week_before_midsummer):
            response = self.client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count)

    def test_new_event_creation_during_midsummer_week(self):
        two_days_before_midsummer = get_midsummer_saturday(2019) - datetime.timedelta(days=2)
        event_count = Event.objects.count()
        with mock.patch('juhannus.models.timezone.now', return_value=two_days_before_midsummer):
            response = self.client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count + 1)

    def test_new_event_creation_by_seconds(self):
        sat = get_midsummer_saturday(2019)
        sun_evening = sat.replace(hour=23, minute=59, second=59) - datetime.timedelta(days=6)
        event_count = Event.objects.count()
        with mock.patch('juhannus.models.timezone.now', return_value=sun_evening):
            response = self.client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count)
        with mock.patch('juhannus.models.timezone.now', return_value=sun_evening + datetime.timedelta(seconds=2)):
            response = self.client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count + 1)

    def test_endpoints(self):
        response = self.client.get(reverse("juhannus:event-latest"))
        self.assertEqual(response.status_code, 200)
        response = self.client.get("asdf")
        self.assertEqual(response.status_code, 404)

    def test_post_insert_record_past_deadline(self):
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = self.client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.count(), original_count)

    def test_post_insert_record_prior_deadline(self):
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        now_in_past = timezone.now().replace(year=Event.objects.first().year - 1, month=1, day=1)
        with mock.patch('juhannus.models.timezone.now', return_value=now_in_past):
            response = self.client.post(endpoint, {**form.data, **{"action": "save"}})
            self.assertEqual(response.status_code, 302)
            self.assertGreater(Participant.objects.count(), original_count)

    def test_post_insert_record_past_deadline_superuser(self):
        self.client.login(username='superuser', password='123')
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = self.client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)

    def test_post_modify_record_normal_user(self):
        original_count = Participant.objects.count()
        self.client.login(username='superuser', password='123')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = self.client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)
        self.client.logout()
        form.data["name"] = "abcd"
        response = self.client.post(endpoint, {**form.data, **{"action": "modify", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.last().name, "abc")

    def test_post_modify_record_superuser(self):
        original_count = Participant.objects.count()
        self.client.login(username='superuser', password='123')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = self.client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)
        form.data["name"] = "abcd"
        response = self.client.post(endpoint, {**form.data, **{"action": "modify", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.last().name, "abcd")

    def test_post_delete_record_normal_user(self):
        self.client.login(username='superuser', password='123')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = self.client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        new_count = Participant.objects.count()
        self.client.logout()
        response = self.client.post(endpoint, {**form.data, **{"action": "delete", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.count(), new_count)

    def test_post_delete_record_superuser(self):
        original_count = Participant.objects.count()
        self.client.login(username='superuser', password='123')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = self.client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)
        response = self.client.post(endpoint, {**form.data, **{"action": "delete", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertLess(Participant.objects.last().name, "abcd")
