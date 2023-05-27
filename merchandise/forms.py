from django import forms

from .models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'desc', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'desc': forms.Textarea(attrs={'class': 'textarea'}),
            'price': forms.NumberInput(attrs={'class': 'input'}),
        }
