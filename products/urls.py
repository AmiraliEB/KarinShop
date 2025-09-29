from django.urls import path
from .views import ProductDetailView, post_redirect_view
from .models import Product

app_name = 'products'

urlpatterns = [
    #TODO: change the url pattern to use slug on product full_name
    path('product-<int:pk>/', post_redirect_view, name='post_redirect'),
    path('product-<int:pk>/<slug:slug>', ProductDetailView.as_view(), name='product-detail'),
]