import pytest
from django.urls import reverse
from model_bakery import baker
from orders.models import Coupon, Order


@pytest.mark.django_db
class TestDemoGatewayView:
    def test_gateway_view_renders_correctly(self, client, django_user_model):
        user = baker.make(django_user_model)
        client.force_login(user)

        order = baker.make(Order, user=user, order_number="123-ABC")
        baker.make("orders.OrderItem", order=order, price=1000, quantity=1)

        url = reverse("demo-gateway")
        response = client.get(url, {"order_number": order.order_number})

        assert response.status_code == 200
        assert response.context["amount"] == 1000
        assert response.context["order_number"] == "123-ABC"

    def test_gateway_view_with_coupon(self, client, django_user_model):
        user = baker.make(django_user_model)
        client.force_login(user)

        coupon = baker.make(Coupon, discount_type="v", discount_value=200)
        order = baker.make(Order, user=user, order_number="COUPON-TEST")
        baker.make("orders.OrderItem", order=order, price=1000, quantity=1)

        session = client.session
        session["coupon_id"] = coupon.id
        session.save()

        url = reverse("demo-gateway")
        response = client.get(url, {"order_number": order.order_number})
        assert response.context["amount"] == 800


@pytest.mark.django_db
class TestPaymentVerifyView:
    def test_verify_success(self, client, django_user_model):
        user = baker.make(django_user_model)
        product = baker.make("products.Product", stock=5)
        order = baker.make(Order, user=user, order_number="ORDER-SUCCESS-TEST", is_paid=False)
        baker.make("orders.OrderItem", order=order, product=product, quantity=1, price=1000)

        url = reverse("verify")

        data = {"success": "1", "order_number": order.order_number, "ref_id": "123456789", "amount": "1000"}

        response = client.post(url, data)

        assert response.status_code == 200
        assert "payments/successful-payment.html" in [t.name for t in response.templates]

        order.refresh_from_db()
        assert order.is_paid is True
        assert order.status == "c"

    def test_verify_failure(self, client):
        url = reverse("verify")
        data = {"ref_id": "123456", "amount": "1000", "failure": "true"}
        response = client.post(url, data)
        assert response.status_code == 200
        assert "payments/failed-payment.html" in [t.name for t in response.templates]
