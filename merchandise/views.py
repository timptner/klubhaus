from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy

from .forms import ProductForm
from .models import Product


class ProductListView(LoginRequiredMixin, ListView):
    model = Product


class ProductCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'merchandise.add_product'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('merchandise:product_list')
    success_message = "%(name)s wurde erfolgreich erstellt"


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
