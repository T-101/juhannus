from django import forms

from juhannus.models import Participant


class SubmitForm(forms.ModelForm):

    def clean(self):
        if self.data.get("action") == "delete":
            return self.cleaned_data

        name = self.cleaned_data.get("name")
        event = self.cleaned_data.get("event")
        if event.get_participants().filter(name__iexact=name.strip()):
            raise forms.ValidationError({"name": "Name already in use. Choose another"})

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
