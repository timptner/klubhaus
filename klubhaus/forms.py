from django.forms.renderers import TemplatesSetting


class BulmaFormRenderer(TemplatesSetting):
    form_template_name = 'bulma/form_layout.html'
