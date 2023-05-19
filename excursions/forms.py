from django import forms
from django.core.exceptions import ValidationError

from klubhaus.mails import PostmarkTemplate

from .models import Excursion, Participant


class ExcursionForm(forms.ModelForm):
    class Meta:
        model = Excursion
        fields = ['title', 'location', 'date', 'desc', 'ask_for_car', 'website', 'image', 'state']
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
            'ask_for_car': "Teilnehmer müssen eine Angabe darüber machen, ob sie ein Auto besitzen und wie viele "
                           "Plätze das Auto hat.",
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


class ExtendedParticipantForm(ParticipantForm):
    class Meta:
        model = Participant
        fields = ['is_driver', 'seats', 'comment']
        labels = {
            'is_driver': "Auto-Besitzer",
        }
        widgets = {
            'is_driver': forms.RadioSelect(choices=[(True, "Ja"), (False, "Nein")]),
            'seats': forms.NumberInput(attrs={'class': 'input'}),
            'comment': forms.Textarea(attrs={'class': 'textarea'}),
        }
        help_texts = {
            'is_driver': "Du besitzt ein Auto und wärst bereit, eine Fahrgemeinschaft zu bilden.<br>"
                         "Bitte gib deine IBAN im Bemerkungsfeld ein, falls du dieses Feld mit \"Ja\" beantwortest.",
            'seats': "Die Anzahl der verfügbaren Sitzplätze im Auto <strong>inklusive</strong> Fahrer."
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_driver'].required = True
        self.fields['seats'].required = False

        self.initial.update({
            'is_driver': False,
            'seats': 0,
        })

    def clean_seats(self):
        data = self.cleaned_data['seats']

        if data is None:
            data = 0

        return data

    def clean(self):
        cleaned_data = super().clean()

        is_driver = cleaned_data.get('is_driver')
        seats = cleaned_data.get('seats')

        if is_driver is not None and seats is not None:
            if is_driver and seats < 1:
                self.add_error('seats', ValidationError(
                    "Da du ein Auto besitzt muss diese Zahl größer 0 sein.",
                    code='number_to_small',
                ))

            if is_driver and seats > 9:
                self.add_error('seats', ValidationError(
                    "Du darfst als Fahrer maximal 8 weitere Personen befördern. "
                    "Diese Zahl muss somit kleiner als 9 sein.",
                    code='number_to_big',
                ))

            if not is_driver and seats != 0:
                self.add_error('seats', ValidationError(
                    "Da du kein Auto besitzt muss dieses Feld den Wert 0 haben oder leer gelassen werden.",
                    code='seats_must_be_zero',
                ))


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


class ParticipantContactForm(forms.Form):
    ALL = 'all'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    DRIVERS_APPROVED = 'approved-drivers'
    DRIVERS_REJECTED = 'rejected-drivers'

    RECIPIENTS_CHOICES = [
        (ALL, "Alle Teilnehmer"),
        (APPROVED, "Zugelassene Teilnehmer"),
        (REJECTED, "Abgelehnte Teilnehmer"),
        (DRIVERS_APPROVED, "Zugelassene Teilnehmer mit Fahrzeug"),
        (DRIVERS_REJECTED, "Abgelehnte Teilnehmer mit Fahrzeug"),
    ]

    recipients = forms.ChoiceField(
        label="Empfänger",
        choices=RECIPIENTS_CHOICES,
    )

    message = forms.CharField(
        label="Nachricht",
        widget=forms.Textarea(attrs={'class': 'textarea'}),
    )

    def __init__(self, *args, **kwargs):
        self.excursion = kwargs.pop('excursion')
        super().__init__(*args, **kwargs)

        if not self.excursion.ask_for_car:
            self.fields['recipients'].choices = self.RECIPIENTS_CHOICES[:3]

    def clean_recipients(self):
        data = self.cleaned_data['recipients']

        participants = self._get_queryset()

        if not participants.exists():
            raise ValidationError("Bitte wähle eine Gruppe von Empfängern, welche mehr als 0 Mitglieder besitzt.")

        return data

    def _get_queryset(self):
        recipient_list = self.cleaned_data['recipients']

        participants = Participant.objects.filter(excursion=self.excursion)

        if recipient_list == self.ALL:
            pass
        elif recipient_list == self.APPROVED:
            participants = participants.filter(state=Participant.APPROVED)
        elif recipient_list == self.REJECTED:
            participants = participants.filter(state=Participant.REJECTED)
        elif recipient_list == self.DRIVERS_APPROVED:
            participants = participants.filter(state=Participant.APPROVED).filter(is_driver=True)
        elif recipient_list == self.DRIVERS_REJECTED:
            participants = participants.filter(state=Participant.REJECTED).filter(is_driver=True)
        else:
            raise Exception("Unknown recipient list")

        return participants

    def send_mail(self):
        message = self.cleaned_data['message']

        participants = self._get_queryset()

        template = PostmarkTemplate()

        payloads = []
        recipients = []
        for participant in participants:
            user = participant.user
            excursion = participant.excursion

            recipients.append(user.email)

            context = {
                'first_name': user.first_name,
                'excursion': excursion.title,
                'body': message,
            }
            payloads.append(context)

        template.send_message_batch(recipients, payloads, template_alias='contact-participants')
