import datetime
from unittest import mock

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from juhannus.models import Event, Participant, get_midsummer_saturday
from juhannus.forms import SubmitForm


class ViewsTests(TestCase):
    fixtures = ['juhannus/tests/juhannus.json']

    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(username="user", email="user@example.com",
                                                                    password="test")

    def tearDown(self):
        del self.admin_user

    def test_empty_db(self):
        client = Client()
        endpoint = reverse("juhannus:event-latest")
        self.assertEqual(endpoint, "/")
        with mock.patch('juhannus.models.Event', new=Event.objects.all().delete()):
            response = client.get(endpoint)
            self.assertEqual(response.content, b"No event in db")
            self.assertEqual(response.status_code, 200)

    def test_new_event_creation_prior_midsummer_week(self):
        client = Client()
        week_before_midsummer = get_midsummer_saturday(2019) - datetime.timedelta(days=7)
        event_count = Event.objects.count()
        with mock.patch('juhannus.models.timezone.now', return_value=week_before_midsummer):
            response = client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count)

    def test_new_event_creation_during_midsummer_week(self):
        client = Client()
        two_days_before_midsummer = get_midsummer_saturday(2019) - datetime.timedelta(days=2)
        event_count = Event.objects.count()
        with mock.patch('juhannus.models.timezone.now', return_value=two_days_before_midsummer):
            response = client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count + 1)

    def test_new_event_creation_by_seconds(self):
        client = Client()
        sat = get_midsummer_saturday(2019)
        sun_evening = sat.replace(hour=23, minute=59, second=59) - datetime.timedelta(days=6)
        event_count = Event.objects.count()
        with mock.patch('juhannus.models.timezone.now', return_value=sun_evening):
            response = client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count)
        with mock.patch('juhannus.models.timezone.now', return_value=sun_evening + datetime.timedelta(seconds=2)):
            response = client.get(reverse("juhannus:event-latest"))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(Event.objects.count(), event_count + 1)

    def test_endpoints(self):
        client = Client()
        response = client.get(reverse("juhannus:event-latest"))
        self.assertEqual(response.status_code, 200)
        response = client.get("asdf")
        self.assertEqual(response.status_code, 404)

    def test_post_insert_record_past_deadline(self):
        client = Client()
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.count(), original_count)

    def test_post_insert_record_prior_deadline(self):
        client = Client()
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        now_in_past = timezone.now().replace(year=Event.objects.first().year - 1, month=1, day=1)
        with mock.patch('juhannus.models.timezone.now', return_value=now_in_past):
            response = client.post(endpoint, {**form.data, **{"action": "save"}})
            self.assertEqual(response.status_code, 302)
            self.assertGreater(Participant.objects.count(), original_count)

    def test_post_insert_record_past_deadline_superuser(self):
        client = Client()
        client.login(username='user', password='test')
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)

    def test_post_modify_record_normal_user(self):
        original_count = Participant.objects.count()
        client = Client()
        client.login(username='user', password='test')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)
        client = Client()
        form.data["name"] = "abcd"
        response = client.post(endpoint, {**form.data, **{"action": "modify", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.last().name, "abc")

    def test_post_modify_record_superuser(self):
        original_count = Participant.objects.count()
        client = Client()
        client.login(username='user', password='test')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)
        form.data["name"] = "abcd"
        response = client.post(endpoint, {**form.data, **{"action": "modify", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.last().name, "abcd")

    def test_post_delete_record_normal_user(self):
        client = Client()
        client.login(username='user', password='test')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        new_count = Participant.objects.count()
        client = Client()
        response = client.post(endpoint, {**form.data, **{"action": "delete", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Participant.objects.count(), new_count)

    def test_post_delete_record_superuser(self):
        original_count = Participant.objects.count()
        client = Client()
        client.login(username='user', password='test')
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        endpoint = reverse("juhannus:event-latest")
        response = client.post(endpoint, {**form.data, **{"action": "save"}})
        self.assertEqual(response.status_code, 302)
        self.assertGreater(Participant.objects.count(), original_count)
        response = client.post(endpoint, {**form.data, **{"action": "delete", "pk": 2}})
        self.assertEqual(response.status_code, 302)
        self.assertLess(Participant.objects.last().name, "abcd")
