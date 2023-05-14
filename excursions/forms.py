from django import forms
from django.core.exceptions import ValidationError

from .models import Excursion, Participant


class ExcursionForm(forms.ModelForm):
    class Meta:
        model = Excursion
        fields = ['title', 'location', 'date', 'desc', 'website', 'image', 'state']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'location': forms.TextInput(attrs={'class': 'input'}),
            'date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'desc': forms.Textarea(attrs={'class': 'textarea'}),
            'website': forms.URLInput(attrs={'class': 'input'}),
            'image': forms.FileInput(attrs={'class': 'file-input'}),
            'state': forms.RadioSelect,
        }
        help_texts = {
            'desc': "Du kannst dieses Feld in der rechten unteren Ecke größer ziehen.",
            'image': "Ideal ist ein Bild vom Werksgelände oder aus deren Produktion. Bitte vorher die Genehmigung des "
                     "Unternehmens einholen!",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'date' in self.initial:
            # Convert date into iso format string to avoid localization
            self.initial['date'] = self.initial['date'].isoformat()


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'textarea'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.excursion = kwargs.pop('excursion')
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        participant = super().save(commit=False)
        participant.user = self.user
        participant.excursion = self.excursion

        if commit:
            participant.save()

        return participant


ENROLLED_DISPLAY = dict(Participant.STATE_CHOICES).get(Participant.ENROLLED)


class ParticipantStateForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['state']
        widgets = {
            'state': forms.RadioSelect,
        }

    def clean_state(self):
        data = self.cleaned_data['state']

        if data == Participant.ENROLLED:
            raise ValidationError(
                "Der Status \"%(state)s\" kann nur durch einen Administrator gesetzt werden.",
                params={'state': ENROLLED_DISPLAY},
                code='forbidden state',
            )

        return data

    def save(self, commit=True):
        if commit is False:
            raise NotImplementedError("A changed team status will be committed immediately")

        state = self.cleaned_data['state']
        self.instance.set_state(state)

        return self.instance
