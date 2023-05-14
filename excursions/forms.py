from django import forms

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
