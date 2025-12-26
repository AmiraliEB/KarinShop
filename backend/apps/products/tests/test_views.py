import pytest
from django.urls import reverse
from django.conf import settings


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

def get_valid_comment_data():
    return {
        "title": "test_comment",
        "content": "test_content",
        "rating": 4,
        "is_recommend": True,
        "comment_submit": ""
    }

@pytest.mark.django_db
def test_anonymous_user_cannot_comment(client, product_factory):
    product = product_factory()
    url = reverse("products:product_detail", kwargs={"pk":product.id, "slug":"test-slug"})
    data = get_valid_comment_data()

    response = client.post(url,data)

    assert response.status_code == 302
    assert settings.LOGIN_URL in response.url


@pytest.mark.django_db
@pytest.mark.parametrize("override_data, expected_status", [
    ({}, 302),
    ({"title": ""}, 200),
    ({"rating": -1}, 200),
    ({"rating": 6}, 200),
])
def test_add_comment(client,product_factory,user_factory,override_data, expected_status):
    product = product_factory()
    url = reverse("products:product_detail", kwargs={"pk":product.id, "slug":"test-slug"})
    data = get_valid_comment_data()
    data.update(override_data)

    user = user_factory()
    client.force_login(user)

    response = client.post(url,data)
    assert response.status_code == expected_status

    from products.models import Comments
    comment = Comments.objects.filter(parent_product=product.parent_product, user=user).first()
    if expected_status == 302:
        assert comment is not None
        assert comment.title == data['title']
        assert comment.content == data['content']
        assert comment.rating == data['rating']
        assert comment.is_recommend is data['is_recommend']
        assert comment.user == user
    else:
        assert comment is None
        assert response.context['comment_form'].errors