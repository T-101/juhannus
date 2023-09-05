import re
import datetime

from string import Template

from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone


def get_midsummer_saturday(year):
    # Midsummer saturday is always between june 20-26
    day = 20
    while datetime.datetime(year, 6, day).weekday() != 5:
        day += 1
    # return pytz.timezone(settings.TIME_ZONE).localize(datetime.datetime(year, 6, day))
    return timezone.localtime().replace(year=year, month=6, day=day, minute=0, hour=0, second=0, microsecond=0)


class Header(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title


class Body(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title


class Event(models.Model):
    year = models.IntegerField()

    header = models.ForeignKey(Header, on_delete=models.CASCADE, related_name='events')
    body = models.ForeignKey(Body, on_delete=models.CASCADE, related_name='events')

    result = models.PositiveIntegerField(blank=True, null=True)
    is_final = models.BooleanField(default=False)

    def get_midsummer_saturday(self, year=None):
        # Midsummer saturday is always between june 20-26
        if not year:
            year = self.year
        return get_midsummer_saturday(year)

    def get_voting_deadline(self, year=None):
        sat = self.get_midsummer_saturday(year)
        thu = sat - datetime.timedelta(days=2)
        return thu.replace(hour=23, minute=59, second=59)

    def get_results_deadline(self, year=None):
        sat = self.get_midsummer_saturday(year)
        sun = sat + datetime.timedelta(days=1)
        return sun.replace(hour=22, minute=00, second=00)

    def is_voting_available(self, year=None):
        deadline = self.get_voting_deadline(year)
        # use .localtime() when comparing to an aware datetime object
        return timezone.localtime() <= deadline

    def _subst_text(self, text):
        year = re.sub(r'0', "o", str(self.year))  # Replace all zeros with lowercase o's. ASCII art, bitch!
        date_format = "%d.%-m"  # 24.6
        substitutions = {
            'year': year,
            'year_spaced': re.sub(r'(.)', r" \1", year).strip(),
            'results_deadline': self.get_results_deadline().strftime(date_format),
            'voting_deadline': self.get_voting_deadline().strftime(date_format)
        }

        tmp_str = Template(text)
        return tmp_str.safe_substitute(substitutions)

    def get_header_text(self):
        return self._subst_text(self.header.text)

    def get_body_text(self):
        return self._subst_text(self.body.text)

    def __str__(self):
        return f"Midsummer {self.year}"


class Participant(models.Model):
    name = models.CharField(max_length=32,
                            validators=[RegexValidator(
                                regex=r'^[\w\/\s^\-\.,\\\|\(\)\[\]\{\}&!\"#€%&/=?@£$∞§|≈±+:;<>´`¨\*]+$',
                                message='Invalid letter found',
                                code='invalid_letter'
                            )]
                            )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    vote = models.PositiveIntegerField(validators=[
        MaxValueValidator(100),
        MinValueValidator(0)
    ])

    created = models.DateTimeField(auto_now_add=True)
    visible = models.BooleanField(default=True)

    def __str__(self):
        return self.name
