import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_product_detail_view_loads(client, product_factory):
    product = product_factory()
    url = reverse('products:product_detail', kwargs={'pk': product.pk, 'slug': 'test-slug'})
    response = client.get(url)
    assert response.status_code == 200

    assert response.context['product'] == product
    assert 'products/product_details.html' in [t.name for t in response.templates]


@pytest.mark.django_db
def test_add_to_cart_from_product_page(client, product_factory):
    product = product_factory()
    url = reverse('products:product_detail', kwargs={'pk': product.pk, 'slug': 'test-slug'})

    data = {
        'cart_submit': '',
        'quantity': 3
    }
    response = client.post(url, data)

    assert response.status_code == 302 

    session = client.session
    assert str(product.id) in session['cart']
    assert session['cart'][str(product.id)]['quantity'] == 3