from unittest import mock

from django.test import TestCase, Client
from django.urls import reverse

from juhannus.models import Event


class ViewsTests(TestCase):
    fixtures = ['juhannus/tests/juhannus.json']

    def test_empty_db(self):
        client = Client()
        endpoint = reverse("juhannus:event-latest")
        self.assertEqual(endpoint, "/")
        with mock.patch('juhannus.models.Event', new=Event.objects.all().delete()):
            response = client.get(endpoint)
            self.assertEqual(response.content, b"No event in db")
            self.assertEqual(response.status_code, 200)

    def test_endpoints(self):
        client = Client()
        response = client.get(reverse("juhannus:event-latest"))
        self.assertEqual(response.status_code, 200)
        response = client.get("asdf")
        self.assertEqual(response.status_code, 404)
