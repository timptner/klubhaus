from django.forms import ModelForm as BaseModelForm
from django.forms.widgets import DateInput


class ModelForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ''
        for key, value in self.initial.items():
            if type(self.fields[key].widget) is DateInput:
                self.initial[key] = str(value)
