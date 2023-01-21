from django.views.generic import TemplateView


class LandingPage(TemplateView):
    template_name = 'home/landing_page.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['companies'] = [
            {'name': "Sket GmbH", 'image': "home/sket.jpg", 'url': "https://www.sket.de/"},
            {'name': "HORIBA FuelCon GmbH", 'image': "home/horiba.jpg", 'url': "https://www.horiba-fuelcon.com/"},
            {'name': "Fendt GmbH", 'image': "home/fendt.jpg", 'url': "https://www.fendt.com/"},
        ]
        return context
