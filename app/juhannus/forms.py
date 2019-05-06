from django import forms

from juhannus.models import Participant


class SubmitForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ('name', 'vote', 'event')
        labels = {
            'name': '',
            'vote': ''
        }

        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': ' Handle',
                'autocomplete': "off",
                'autofocus': 'autofocus'}),
            'vote': forms.NumberInput(attrs={
                'placeholder': ' Vote',
                'autocomplete': "off",
                'min': 0,
                'max': 100})
        }
        error_messages = {
            'handle': {
                'required': 'Tää sun handle olis vähän niinku tarpeellinen tieto.',
                'invalid': 'Ai sä meinasit ettei bäkkäri validoi näitä kans?',
                'unique': 'Näin lyhyt handlelista ja silti osuit dupeen. Yritä ny ees.'
            },
            'amount': {
                'min_value': '0-100 kelpaa. Kyl sä pystyt siihen.',
                'max_value': '0-100 kelpaa. Kyl sä pystyt siihen.',
                'invalid': 'Ai sä meinasit ettei bäkkäri validoi näitä kans? 0-100 plx'
            }}
