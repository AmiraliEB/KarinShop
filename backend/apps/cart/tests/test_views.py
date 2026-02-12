import pytest
from accounts.models import Address
from cart.models import Cart, CartItem
from django.urls import reverse
from model_bakery import baker
from orders.models import Order


@pytest.mark.django_db
def test_cart_detail_view_loads(client):
    response = client.get("/cart/")

    assert response.status_code == 200
    assert "cart/cart.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_htmx_update_cart_item(client):
    product = baker.make("products.Product", stock=10)
    session = client.session
    session["cart"] = {str(product.id): {"quantity": 1, "price": 100000}}
    session.save()

    url = reverse("update_cart_item", args=["add", product.id])
    response = client.post(url, **{"HTTP_HX_REQUEST": "true"})
    assert response.context["item_quantity"] == 2
    assert response.status_code == 200
    assert response.context["product_obj"] == product
    assert response.context["product_available_in_cart"] is True

    session = client.session
    assert session["cart"][str(product.id)]["quantity"] == 2

    url = reverse("update_cart_item", args=["decrement", product.id])
    response = client.post(url, **{"HTTP_HX_REQUEST": "true"})

    assert response.context["item_quantity"] == 1
    assert response.status_code == 200
    assert response.context["product_obj"] == product
    assert response.context["product_available_in_cart"] is True

    session = client.session
    assert session["cart"][str(product.id)]["quantity"] == 1

    url = reverse("update_cart_item", args=["remove", product.id])
    response = client.post(url, **{"HTTP_HX_REQUEST": "true"})
    assert response.context["item_quantity"] == 0
    assert response.status_code == 200
    assert response.context["product_obj"] == product
    assert response.context["product_available_in_cart"] is False

    session = client.session
    assert str(product.id) not in session["cart"]


@pytest.mark.django_db
class TestPaymentView:
    def test_payment_view_redirects_if_no_address(self, client, django_user_model):
        user = baker.make(django_user_model)
        client.force_login(user)

        url = reverse("payment")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("checkout")

    def test_payment_view_redirects_if_empty_cart(self, client, django_user_model):
        user = baker.make(django_user_model)
        client.force_login(user)
        baker.make(Address, user=user)
        baker.make(Cart, user=user)

        url = reverse("payment")
        response = client.get(url)

        assert response.status_code == 302
        assert response.url == reverse("cart_detail")

    def test_payment_view_creates_order_success(self, client, django_user_model):
        user = baker.make(django_user_model)
        client.force_login(user)
        product = baker.make("products.Product", stock=10, initial_price=1000, discount_value=0)
        baker.make(Address, user=user)
        cart = baker.make(Cart, user=user)
        baker.make(CartItem, cart=cart, quantity=1, product=product)

        url = reverse("payment")
        response = client.get(url)

        assert response.status_code == 200
        assert "payment_url" in response.context
        assert Order.objects.filter(user=user).exists()
        assert response.context["total_price"] == 1000
