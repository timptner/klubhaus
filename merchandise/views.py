from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView
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
    success_message = "%(name)s erfolgreich erstellt"


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product


class ProductUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'merchandise.change_product'
    model = Product
    form_class = ProductForm
    success_message = "%(name)s erfolgreich aktualisiert"

    def get_success_url(self):
        return reverse_lazy('merchandise:product_detail', kwargs={'pk': self.kwargs['pk']})
