from django.urls import path
from . import views

urlpatterns = [
    path('',views.CartView.as_view(),name='cart_detail'),
    path('clear',views.clear_items_form_cart,name='cart_clear_item'),
    path('checkout',views.CheckoutView.as_view(),name='checkout'),
    path('checkout/payment',views.PaymentView.as_view(),name='payment'),

    path('remove-coupon',views.remove_coupon, name='remove_coupon'),
    path('apply-coupon',views.apply_coupon, name='apply_coupon'),

    path('increase-nav/<int:pk>',views.add_item, name='add_item'),
    path('decrement-nav/<int:pk>',views.decrement_item, name='decrement_item'),
    path('increase-main/<int:pk>',views.add_item_for_main_cart, name='increase_main_cart'),
    path('decrement-main/<int:pk>',views.decrement_item_for_main_cart, name='decrement_main_cart'),

    path('remove-main/<int:pk>',views.remove_item_form_main_cart,name='cart_remove_main'),
    
    path('clear-items',views.clear_items_form_cart, name='clear_items'),


    
    path('increase-detail/<int:pk>',views.add_item_for_detail_cart, name='increase_detail_cart'),
    path('decrement-detail/<int:pk>',views.decrement_item_for_detail_cart, name='decrement_detail_cart'),
    path('update/<str:action>/<int:pk>', views.update_cart_item, name='update_cart_item'),

]
