from django import forms
from django.core.exceptions import ValidationError
from volunteers.models import Event, Volunteer
from klubhaus.mails import PostmarkTemplate


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'date', 'teaser', 'desc', 'state', 'has_visible_counter']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'teaser': forms.Textarea(attrs={'class': 'textarea', 'rows': 2}),
            'desc': forms.Textarea(attrs={'class': 'textarea'}),
            'state': forms.RadioSelect,
        }
        help_texts = {
            'teaser': "Maximal 500 Zeichen.",
            'desc': "Du kannst <a href=\"https://www.markdownguide.org/cheat-sheet/\" target=\"_blank\">MarkDown</a> "
                    "zur Formatierung nutzen.",
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


class VolunteerContactForm(forms.Form):
    message = forms.CharField(label="Nachricht", widget=forms.Textarea(attrs={'class': 'textarea'}))

    def send_mail(self, event: Event):
        template = PostmarkTemplate()

        volunteers = Volunteer.objects.filter(event=event)

        message = self.cleaned_data['message']

        recipients = []
        payloads = []
        for volunteer in volunteers:
            recipients.append(volunteer.user.email)
            payload = {
                'volunteer_name': volunteer.user.first_name,
                'event_name': event.title,
                'body': message,
            }
            payloads.append(payload)

        errors = template.send_message_batch(recipients, payloads, 'volunteer-contact')
        return errors
