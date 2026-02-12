import pytest
from django.conf import settings
from django.urls import reverse
from model_bakery import baker


@pytest.mark.django_db
def test_product_detail_view_loads(client):
    product_variant = baker.make("products.ProductVariant")
    # this is for reverse relation to work in template and avoid N+1 query
    baker.make("products.Product", product_variant=product_variant)

    url = reverse("products:product_detail", kwargs={"pk": product_variant.pk, "slug": "test-slug"})
    response = client.get(url)
    assert response.status_code == 200

    first_product = product_variant.products.first()
    assert response.context["first_product"] == first_product
    assert response.context["product_counts"] == product_variant.products.count()

    assert "products/product_details.html" in [t.name for t in response.templates]


def get_valid_comment_data():
    return {"title": "test_comment", "content": "test_content", "rating": 4, "is_recommend": True, "comment_submit": ""}


@pytest.mark.django_db
def test_anonymous_user_cannot_comment(client):
    product_variant = baker.make("products.ProductVariant")
    url = reverse("products:product_detail", kwargs={"pk": product_variant.id, "slug": "test-slug"})
    data = get_valid_comment_data()

    response = client.post(url, data)

    assert response.status_code == 302
    assert settings.LOGIN_URL in response.url


@pytest.mark.django_db
@pytest.mark.parametrize(
    "override_data, expected_status",
    [
        ({}, 302),
        ({"title": ""}, 200),
        ({"rating": -1}, 200),
        ({"rating": 6}, 200),
    ],
)
def test_add_comment(client, user_factory, override_data, expected_status):
    product_parent = baker.make("products.ProductParent")
    product_variant = baker.make("products.ProductVariant", parent_product=product_parent)
    baker.make("products.Product", product_variant=product_variant)
    url = reverse("products:product_detail", kwargs={"pk": product_variant.id, "slug": "test-slug"})
    data = get_valid_comment_data()
    data.update(override_data)

    user = user_factory()
    client.force_login(user)

    response = client.post(url, data)
    assert response.status_code == expected_status

    from products.models import Comments

    comment = Comments.objects.filter(parent_product=product_parent, user=user).first()
    if expected_status == 302:
        assert comment is not None
        assert comment.title == data["title"]
        assert comment.content == data["content"]
        assert comment.rating == data["rating"]
        assert comment.is_recommend is data["is_recommend"]
        assert comment.user == user
    else:
        assert comment is None
        assert response.context["comment_form"].errors


@pytest.mark.django_db
@pytest.mark.parametrize(
    "quantity, expected_status",
    [
        (2, 302),
        (-1, 200),
    ],
)
def test_add_cart(client, quantity, expected_status):
    product_variant = baker.make("products.ProductVariant")
    baker.make("products.Product", product_variant=product_variant)
    url = reverse("products:product_detail", kwargs={"pk": product_variant.id, "slug": "test-slug"})
    data = {
        "cart_submit": "",
        "quantity": quantity,
    }

    response = client.post(url, data)
    assert response.status_code == expected_status
    if expected_status == 302:
        session = client.session
        cart = session.get("cart", {})
        product_id = str(product_variant.id)

        assert product_id in cart
        assert cart[product_id]["quantity"] == data["quantity"]

    elif expected_status == 200:
        assert "cart_form" in response.context
        assert response.context["cart_form"].errors

        session = client.session
        cart = session.get("cart", {})
        product_id = str(product_variant.id)
        assert product_id not in cart
