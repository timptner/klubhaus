from django import forms
from django.core.exceptions import ValidationError
from volunteers.models import Event, Volunteer


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'desc', 'state']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'desc': forms.Textarea(attrs={'class': 'textarea'}),
            'state': forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'date' in self.initial:
            self.initial['date'] = self.initial['date'].isoformat()


class VolunteerForm(forms.ModelForm):
    class Meta:
        model = Volunteer
        fields = ['comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'textarea'}),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

    def clean(self):
        super().clean()

        is_registered = Volunteer.objects.filter(event=self.event, user=self.user).exists()
        if is_registered:
            raise ValidationError("Du bist bereits als Helfer registriert.")

    def save(self, commit=True):
        volunteer = super().save(commit=False)
        volunteer.event = self.event
        volunteer.user = self.user

        if commit:
            volunteer.save()

        return volunteer