from django.urls import path
from . import views

urlpatterns = [
    path('cart/',views.CartView.as_view(),name='cart_detail'),
    path('cart/remove/<int:pk>',views.RemoveCartItemView.as_view(),name='cart_remove_item'),
    path('cart/clear',views.RemoveCartItemView.as_view(),name='cart_clear_item'),
    path('cart/checkout',views.CheckoutView.as_view(),name='checkout'),
]
