from django import forms
from django.core.exceptions import ValidationError

from .models import Product, Image, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'desc', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'desc': forms.Textarea(attrs={'class': 'textarea'}),
            'price': forms.NumberInput(attrs={'class': 'input'}),
        }
        help_texts = {
            'price': "Preis kann nur geändert werden solange alle zugehörigen Bestellungen abgeschlossen sind.",
        }

    def clean_price(self):
        data = self.cleaned_data['price']

        if self.initial:
            uncompleted_orders = Order.objects.filter(product=self.instance).exclude(state=Order.COMPLETED)
            if uncompleted_orders.exists():
                raise ValidationError("Es existieren zugehörige Bestellungen, welche noch nicht abgeschlossen sind.")

        return data


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['title', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input'}),
            'file': forms.FileInput(attrs={'class': 'file-input'}),
        }


class OrderForm(forms.ModelForm):
    is_committed = forms.BooleanField(
        label="Hiermit bestätige ich, dass meine Bestellung verbindlich ist.",
        required=True,
    )

    class Meta:
        model = Order
        fields = ['size']
        widgets = {
            'size': forms.RadioSelect,
        }
