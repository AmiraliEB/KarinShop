from django.urls import path
from .views import CartView, RemoveCartItemView

urlpatterns = [
    path('cart/',CartView.as_view(),name='cart_detail'),
    path('cart/remove/<int:pk>',RemoveCartItemView.as_view(),name='cart_remove_item'),
    path('cart/clear',RemoveCartItemView.as_view(),name='cart_clear_item'),
]
