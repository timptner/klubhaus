from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy

from .forms import ProductForm, ImageForm, OrderCreateForm, OrderStateForm, SizeForm
from .models import Product, Image, Order, Size


class ProductListView(LoginRequiredMixin, ListView):
    model = Product

    def get_queryset(self):
        if self.request.user.is_staff:
            queryset = Product.objects.all()
        else:
            queryset = Product.objects.exclude(size=None)
        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['has_products_missing_sizes'] = Product.objects.filter(size=None).exists()
        return context


class ProductCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'merchandise.add_product'
    model = Product
    form_class = ProductForm
    success_url = reverse_lazy('merchandise:product_list')
    success_message = "%(name)s erfolgreich erstellt"


class ProductDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Product

    def test_func(self):
        product = Product.objects.get(pk=self.kwargs['pk'])

        if self.request.user.is_staff:
            return True

        if product.size_set.exists():
            return True

        return False


class ProductUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'merchandise.change_product'
    model = Product
    form_class = ProductForm
    success_message = "%(name)s erfolgreich aktualisiert"

    def get_success_url(self):
        return reverse_lazy('merchandise:product_detail', kwargs={'pk': self.kwargs['pk']})


class SizeListView(PermissionRequiredMixin, ListView):
    permission_required = 'merchandise.view_size'
    model = Size

    def get_queryset(self):
        product = Product.objects.get(pk=self.kwargs['pk'])
        return Size.objects.filter(product=product)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context


class SizeCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    permission_required = 'merchandise.add_size'
    model = Size
    form_class = SizeForm
    success_message = "Größe %(label)s erfolgreich erstellt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        product = Product.objects.get(pk=self.kwargs['pk'])
        size = form.save(commit=False)
        if form.is_valid():
            size.product = product
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('merchandise:size_list', kwargs={'pk': self.kwargs['pk']})


class SizeUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'merchandise.change_size'
    model = Size
    form_class = SizeForm
    success_message = "Größe %(label)s erfolgreich aktualisiert"

    def get_success_url(self):
        size: Size = self.object
        return reverse_lazy('merchandise:size_list', kwargs={'pk': size.product.pk})


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


class OrderListView(LoginRequiredMixin, ListView):
    model = Order

    def get_queryset(self):
        product = Product.objects.get(pk=self.kwargs['pk'])
        return Order.objects.filter(size__product=product)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        context['statistics'] = {
            'amount_orders': self.object_list.count(),
            'amount_customers': self.object_list.order_by().values('user').distinct().count(),
        }
        return context


class OrderCreateView(LoginRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, CreateView):
    model = Order
    form_class = OrderCreateForm
    success_message = "Bestellung erfolgreich abgeschickt"

    def test_func(self):
        product = Product.objects.get(pk=self.kwargs['pk'])

        if not product.size_set.exists():
            return False

        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product'] = Product.objects.get(pk=self.kwargs['pk'])
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['product'] = Product.objects.get(pk=self.kwargs['pk'])
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('accounts:profile_orders')


class OrderStateUpdateView(PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    permission_required = 'merchandise.change_order'
    model = Order
    form_class = OrderStateForm
    template_name = 'merchandise/order_state_form.html'
    success_message = "Status erfolgreich aktualisiert"

    def form_valid(self, form):
        if form.is_valid():
            order = form.save()
            form.send_mail(order, self.request)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('merchandise:order_list', kwargs={'pk': self.object.size.product.pk})


class OrderStatesView(LoginRequiredMixin, TemplateView):
    template_name = 'merchandise/order_states.html'
