from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import ProductForm, ImageForm
from .models import Product, Image


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


class ImageListView(PermissionRequiredMixin, ListView):
    permission_required = 'merchandise.view_image'
    model = Image

    def get_queryset(self):
        product = Product.objects.get(pk=self.kwargs['pk'])
        return Image.objects.filter(product=product)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context


class ImageCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'merchandise.add_image'
    model = Image
    form_class = ImageForm
    success_message = "%(title)s erfolgreich erstellt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        if form.is_valid():
            product = Product.objects.get(pk=self.kwargs['pk'])

            image: Image = form.save(commit=False)
            image.product = product
            image.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('merchandise:product_detail', kwargs={'pk': self.kwargs['pk']})


class ImageDeleteView(PermissionRequiredMixin, SuccessMessageMixin, DeleteView):
    permission_required = 'merchandise.delete_image'
    model = Image
    success_message = "%(title)s erfolgreich gelöscht"

    def get_context_data(self, **kwargs):
        image: Image = self.object
        context = super().get_context_data(**kwargs)
        context['product'] = image.product
        return context

    def get_success_url(self):
        image: Image = self.object
        return reverse_lazy('merchandise:image_list', kwargs={'pk': image.product.pk})
