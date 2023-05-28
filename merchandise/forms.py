from django import forms

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
