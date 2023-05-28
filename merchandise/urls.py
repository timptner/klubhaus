from django.urls import path

from . import views


app_name = 'merchandise'
urlpatterns = [
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/images/', views.ImageListView.as_view(), name='image_list'),
    path('products/<int:pk>/images/add/', views.ImageCreateView.as_view(), name='image_create'),
    path('products/<int:pk>/orders/', views.OrderListView.as_view(), name='order_list'),
    path('products/<int:pk>/orders/add/', views.OrderCreateView.as_view(), name='order_create'),
    path('images/<int:pk>/delete/', views.ImageDeleteView.as_view(), name='image_delete'),
]
