from django import forms
from django.core.exceptions import ValidationError

from .models import Product, Image, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'desc', 'price', 'is_stocked']
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
            if self.instance.price != data and uncompleted_orders.exists():
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


class OrderCreateForm(forms.ModelForm):
    is_committed = forms.BooleanField(
        label="Hiermit bestätige ich, dass meine Bestellung verbindlich ist.",
        required=True,
    )

    class Meta:
        model = Order
        fields = ['size']
        labels = {
            'size': "Größe",
        }

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        choices = self.product.size_set.values_list('pk', 'label')
        self.fields['size'].widget = forms.Select(choices=choices)

    def save(self, commit=True):
        order = super().save(commit=False)
        order.product = self.product
        order.user = self.user
        if commit:
            order.save()
        return order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['size', 'state']
        widgets = {
            'state': forms.RadioSelect,
        }
