from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from klubhaus.mails import PostmarkTemplate
from tournament.models import Tournament, Team, Player


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


class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')
        self.captain = kwargs.pop('captain')
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data['name']

        is_registered = Team.objects.filter(tournament=self.tournament, captain=self.captain).exists()
        if is_registered:
            raise ValidationError("Du hast bereits ein Team für dieses Turnier angemeldet.")

        if name:
            is_duplicated = Team.objects.filter(tournament=self.tournament, name=name).exists()
            if is_duplicated:
                error = ValidationError("Ein Team mit diesem Namen gibt es bereits.")
                self.add_error('name', error)

    def save(self, commit=True):
        team = super().save(commit=False)
        team.tournament = self.tournament
        team.captain = self.captain
        if commit:
            team.save()
        return team


class PlayerForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input'}),
            'last_name': forms.TextInput(attrs={'class': 'input'}),
        }


ENROLLED_DISPLAY = state = dict(Team.STATE_CHOICES).get(Team.ENROLLED)


class TeamDrawingForm(forms.Form):
    amount = forms.IntegerField(
        label="Anzahl",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'input'}),
        help_text="Die Anzahl der Teams, welche per Los zugelassen werden sollen."
    )

    def __init__(self, *args, **kwargs):
        self.tournament = kwargs.pop('tournament')
        super().__init__(*args, **kwargs)

    def clean_amount(self):
        data = self.cleaned_data['amount']
        team_count = self.tournament.team_set.filter(state=Team.ENROLLED).count()

        if data > team_count:
            raise ValidationError(
                "Es können maximal %(amount)s Teams ausgelost werden, da nur "
                "entsprechend viele Teams den Status \"%(state)s\" besitzen.",
                params={
                    'amount': team_count,
                    'state': ENROLLED_DISPLAY,
                },
                code='maximum integer exceeded',
            )

        return data


class TeamContactForm(forms.Form):
    message = forms.CharField(
        label="Nachricht",
        widget=forms.Textarea(attrs={'class': 'textarea'}),
    )

    def send_email(self, tournament: Tournament) -> dict:
        message = self.cleaned_data['message']

        recipients = []
        payloads = []
        for team in tournament.team_set.filter(state=Team.APPROVED):
            recipients.append(team.captain.email)
            payload = {
                'tournament_name': tournament.title,
                'team_name': team.name,
                'captain_name': team.captain.first_name,
                'body': message,
            }
            payloads.append(payload)

        template = PostmarkTemplate()
        errors = template.send_message_batch(recipients, payloads, 'tournament-info')
        return errors


class TeamStatusForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ['state']
        widgets = {
            'state': forms.RadioSelect,
        }

    def clean_state(self):
        data = self.cleaned_data['state']
        if data == Team.ENROLLED:
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
