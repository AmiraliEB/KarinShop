from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('product-<int:pk>/', views.post_redirect_view, name='post_redirect'),
    path('product-<int:pk>/<str:slug>', views.ProductDetailView.as_view(), name='product_detail'),
]