from django import forms
from django.utils import timezone
from tournament.models import Tournament


class TournamentForm(forms.ModelForm):
    class Meta:
        model = Tournament
        fields = ['title', 'date', 'desc', 'registration_start', 'registration_end']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'desc': forms.Textarea(attrs={'class': 'textarea'}),
            'registration_start': forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'}),
            'registration_end': forms.DateTimeInput(attrs={'class': 'input', 'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.initial:
            self.initial['date'] = self.initial['date'].isoformat()
            for field in ['registration_start', 'registration_end']:
                localtime = timezone.localtime(self.initial[field])
                self.initial[field] = localtime.strftime('%Y-%m-%dT%H:%M:%S')
