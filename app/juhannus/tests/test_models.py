from unittest import mock

from django.test import TestCase
from django.utils import timezone

from juhannus.models import Event, Header, Body, Participant


class ModelsTests(TestCase):
    def setUp(self):
        test_header2018 = Header.objects.create(title="2018", text="Midsummer 2018")
        test_body2018 = Body.objects.create(title="2018", text="$year $year_spaced")
        test_header2020 = Header.objects.create(title="2020", text="Midsummer 2020")
        test_body2020 = Body.objects.create(title="2020", text="$year $year_spaced")
        self.midsummer2018 = Event.objects.create(year=2018, header=test_header2018, body=test_body2018)
        self.midsummer2020 = Event.objects.create(year=2020, header=test_header2020, body=test_body2020)
        self.participant = Participant.objects.create(event=self.midsummer2018,
                                                      name="Asset 463 / Groovy ^ Pier",
                                                      vote=6)

    def test_model_create(self):
        event = self.midsummer2018
        self.assertEqual(event.get_header_text(), "Midsummer 2018")
        self.assertEqual(event.get_body_text(), "2o18 2 o 1 8")
        midsummer_week = event.get_midsummer_saturday().strftime("%W")
        self.assertEqual(midsummer_week, "25")
        self.assertEqual(self.participant.name, "Asset 463 / Groovy ^ Pier")

        event = self.midsummer2020
        self.assertEqual(event.get_header_text(), "Midsummer 2020")
        self.assertEqual(event.get_body_text(), "2o2o 2 o 2 o")

    def test_get_participants(self):
        event = self.midsummer2018
        self.assertEqual(len(event.get_participants()), 1)
        self.assertEqual(event.get_participants().first().vote, 6)
        event = self.midsummer2020
        self.assertEqual(len(event.get_participants()), 0)

    def test_get_saturday(self):
        event = self.midsummer2018
        self.assertEqual(event.get_midsummer_saturday().strftime("%d"), "23")
        event = self.midsummer2020
        self.assertEqual(event.get_midsummer_saturday().strftime("%d"), "20")

    def test_get_voting_deadline(self):
        deadline = self.midsummer2018.get_voting_deadline().isoformat()
        self.assertEqual(deadline, "2018-06-21T23:59:59+03:00")
        deadline = self.midsummer2018.get_voting_deadline(year=2020).isoformat()
        self.assertEqual(deadline, "2020-06-18T23:59:59+03:00")

    def test_get_results_deadline(self):
        deadline = self.midsummer2018.get_results_deadline().isoformat()
        self.assertEqual(deadline, "2018-06-24T22:00:00+03:00")
        deadline = self.midsummer2018.get_results_deadline(year=2020).isoformat()
        self.assertEqual(deadline, "2020-06-21T22:00:00+03:00")

    def test_is_voting_available(self):
        event = self.midsummer2018
        year_in_past = event.get_midsummer_saturday().year - 1
        year_in_future = timezone.now().year + 1
        now_in_past = timezone.now().replace(year=year_in_past, month=1, day=1)
        with mock.patch('juhannus.models.timezone.now', return_value=now_in_past):
            self.assertTrue(event.is_voting_available())
        now_in_future = timezone.now().replace(year=year_in_future, month=1, day=1)
        with mock.patch('juhannus.models.timezone.now', return_value=now_in_future):
            self.assertFalse(event.is_voting_available())
