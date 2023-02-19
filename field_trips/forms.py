from django.utils.translation import gettext_lazy as _
from farafmb.forms import ModelForm
from field_trips.models import FieldTrip


class FieldTripForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.input_type = 'date'

    class Meta:
        model = FieldTrip
        fields = ['title', 'location', 'website', 'image', 'desc', 'date', 'seats']
        help_texts = {
            'desc': _("Use <a href=\"https://www.markdownguide.org/cheat-sheet/\">Markdown</a> to "
                      "format text or add links."),
        }
