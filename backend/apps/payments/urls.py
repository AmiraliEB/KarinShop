from django.urls import path

from .views import demo_gateway_view, payment_verify_view

urlpatterns = [
    path("demo-gateway/", demo_gateway_view, name="demo-gateway"),
    path("verify/", payment_verify_view, name="verify"),
]
