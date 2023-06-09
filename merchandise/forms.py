from django import forms
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.urls import reverse_lazy

from klubhaus.mails import PostmarkTemplate

from .models import Product, Image, Order, Size


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
            uncompleted_orders = Order.objects.filter(size__product=self.instance).exclude(state=Order.COMPLETED)
            if self.instance.price != data and uncompleted_orders.exists():
                raise ValidationError("Es existieren zugehörige Bestellungen, welche noch nicht abgeschlossen sind.")

        return data


class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['label']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'input'}),
        }
        help_texts = {
            'label': "Bezeichnung kann nur geändert werden solange alle zugehörigen Bestellungen abgeschlossen sind.",
        }

    def clean_label(self):
        data = self.cleaned_data['label']

        if self.initial:
            size: Size = self.instance
            uncompleted_orders = Order.objects.filter(size__product=size.product).exclude(state=Order.COMPLETED)
            if self.instance.label != data and uncompleted_orders:
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


class OrderStateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['state']
        widgets = {
            'state': forms.RadioSelect,
        }

    def clean_state(self):
        data = self.cleaned_data['state']
        if data == Order.PENDING:
            state_display = dict(Order.STATE_CHOICES).get(data)
            raise ValidationError("Status kann nicht zu %(state)s geändert werden.", params={'state': state_display})
        return data

    @staticmethod
    def send_mail(order: Order, request: HttpRequest):
        scheme = 'https' if request.is_secure() else 'http'
        domain = request.get_host()

        if order.state == Order.CONFIRMED:
            price = f"{order.size.product.price}".replace('.', ',')

            alias = 'order-confirmed'
            model = {
                'order_id': f"{order.pk:04d}",
                'date': order.created_at.date().isoformat(),
                'order_details': [
                    {
                        'product': order.size.product.name,
                        'size': order.size.label,
                        'amount': price,
                    },
                ],
                'total': price,
                'full_name': order.user.get_full_name(),
            }
        elif order.state == Order.PAID:
            alias = 'order-paid'
            model = {
                'product_name': order.size.product.name,
                'size_label': order.size.label,
                'order_date': order.created_at.strftime('%d.%m.%Y'),
            }
        elif order.state == Order.READY:
            alias = 'order-ready'
            model = {}
        elif order.state == Order.COMPLETED:
            alias = 'order-completed'
            model = {}
        elif order.state == Order.CANCELED:
            alias = 'order-canceled'
            path = reverse_lazy('merchandise:order_states')
            model = {
                'state_url': f"{scheme}://{domain}{path}"
            }
        else:
            raise NotImplementedError("No template for selected order state available")

        path = reverse_lazy('accounts:profile_orders')

        model.update({
            'first_name': order.user.first_name,
            'action_url': f"{scheme}://{domain}{path}",
        })

        template = PostmarkTemplate()
        template.send_message(
            recipient=order.user.email,
            template_alias=alias,
            template_model=model,
        )
