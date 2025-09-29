from django.urls import path
from .views import ProductDetailView, post_redirect_view
from .models import Product

app_name = 'products'

urlpatterns = [
    path('product-<int:pk>/', post_redirect_view, name='post_redirect'),
    path('product-<int:pk>/<str:slug>', ProductDetailView.as_view(), name='product_detail'),
]