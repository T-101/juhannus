from django import forms

from juhannus.models import Participant


class SubmitForm(forms.ModelForm):

    def clean(self):
        action = self.data.get("action")
        if action == "delete":
            return self.cleaned_data

        name = self.cleaned_data.get("name")
        event = self.cleaned_data.get("event")
        if event.participants.filter(name__iexact=name.strip()) and action != "modify":
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
                'id': 'input_handle',
                'placeholder': ' Handle',
                'autocomplete': "off",
                'autofocus': 'autofocus'}),
            'vote': forms.NumberInput(attrs={
                'id': 'id_vote',
                'placeholder': ' Vote',
                'autocomplete': "off",
                'min': 0,
                'max': 100})
        }
