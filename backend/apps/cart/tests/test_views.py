from django.urls import reverse
import pytest

@pytest.mark.django_db
def test_cart_detail_view_loads(client):
    response = client.get("/cart/")

    assert response.status_code == 200
    assert "cart/cart.html" in [template.name for template in response.templates]


@pytest.mark.django_db
def test_htmx_update_cart_item(client, product_factory):
    product = product_factory()
    session = client.session
    session['cart'] = {str(product.id): {'quantity': 1, 'price': 100000}}
    session.save()

    url = reverse('update_cart_item', args=['add', product.id])
    response = client.post(url, **{'HTTP_HX_REQUEST': 'true'})
    assert response.context['item_quantity'] == 2
    assert response.status_code == 200
    assert response.context['product_obj'] == product
    assert response.context['product_available_in_cart'] is True

    session = client.session
    assert session['cart'][str(product.id)]['quantity'] == 2
