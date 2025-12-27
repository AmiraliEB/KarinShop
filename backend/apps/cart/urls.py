from django.urls import path
from . import views

urlpatterns = [
    path("", views.CartView.as_view(), name="cart_detail"),
    path("clear", views.clear_items_form_cart, name="cart_clear_item"),
    path("checkout", views.CheckoutView.as_view(), name="checkout"),
    path("checkout/payment", views.PaymentView.as_view(), name="payment"),
    path("remove-coupon", views.remove_coupon, name="remove_coupon"),
    path("apply-coupon", views.apply_coupon, name="apply_coupon"),
    path("update/<str:action>/<int:pk>", views.update_cart_item, name="update_cart_item"),
    path("update/clear", views.clear_items_form_cart, name="clear_items"),
]
