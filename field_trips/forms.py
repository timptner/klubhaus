from farafmb.forms import ModelForm
from field_trips.models import FieldTrip


class FieldTripForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.input_type = 'date'

    class Meta:
        model = FieldTrip
        fields = ['title', 'desc', 'date', 'seats']
