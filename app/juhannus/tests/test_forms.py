from django.test import TestCase

from juhannus.forms import SubmitForm
from juhannus.models import Participant


class FormsTests(TestCase):
    fixtures = ["test_juhannus_events.json"]

    def test_form_invalid(self):
        form = SubmitForm()
        self.assertFalse(form.is_valid())
        form = SubmitForm(data={"name": "abc°", "vote": 6, "event": 1})  # invalid letter in name
        self.assertFalse(form.is_valid())
        with self.assertRaises(AttributeError):
            # a field value too long causes the field to become null and raises an attribute error
            form = SubmitForm(
                data={"name": "abcdefabcdefabcdefabcdefabcdefabcdefabcdefabcdef", "vote": "6", "event": 1})
            self.assertFalse(form.is_valid())
        form = SubmitForm(data={"name": "abc", "vote": 666, "event": 1})  # too high vote
        self.assertFalse(form.is_valid())
        with self.assertRaises(AttributeError):
            # invalid event number also raises an AttributeError
            form = SubmitForm(data={"name": "abc", "vote": 1, "event": 666})
            self.assertFalse(form.is_valid())

    def test_form_valid(self):
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        self.assertTrue(form.is_valid())

    def test_form_save_error(self):
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc°", "vote": 6, "event": 1})  # invalid name
        with self.assertRaises(ValueError):
            form.save()
        self.assertEqual(Participant.objects.count(), original_count)

    def test_form_save_success(self):
        original_count = Participant.objects.count()
        form = SubmitForm(data={"name": "abc", "vote": 6, "event": 1})
        self.assertTrue(form.is_valid())
        form.save()
        self.assertGreater(Participant.objects.count(), original_count)
