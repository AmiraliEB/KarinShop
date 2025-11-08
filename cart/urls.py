from django.urls import path
from . import views

urlpatterns = [
    path('',views.CartView.as_view(),name='cart_detail'),
    path('remove/<int:pk>',views.RemoveCartItemView.as_view(),name='cart_remove_item'),
    path('clear',views.RemoveCartItemView.as_view(),name='cart_clear_item'),
    path('checkout',views.CheckoutView.as_view(),name='checkout'),
    path('payment',views.PaymentView.as_view(),name='payment'),
]
