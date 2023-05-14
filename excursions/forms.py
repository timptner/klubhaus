from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Excursion


class ExcursionForm(forms.ModelForm):
    class Meta:
        model = Excursion
        fields = ['title', 'location', 'website', 'image', 'desc', 'date', 'seats']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'location': forms.TextInput(attrs={'class': 'input'}),
            'website': forms.URLInput(attrs={'class': 'input'}),
            'image': forms.FileInput(attrs={'class': 'file-input'}),
            'desc': forms.Textarea(attrs={'class': 'textarea'}),
            'date': forms.DateInput(attrs={'class': 'input', 'type': 'date'}),
            'seats': forms.NumberInput(attrs={'class': 'input'}),
        }
        help_texts = {
            'desc': _("Use <a href=\"https://www.markdownguide.org/cheat-sheet/\">Markdown</a> to "
                      "format text or add links."),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'date' in self.initial:
            # Convert date into iso format string to avoid localization
            self.initial['date'] = self.initial['date'].isoformat()
