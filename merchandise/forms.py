from django import forms

from .models import Product, Image


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
