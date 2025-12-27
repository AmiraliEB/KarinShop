import pytest
from cart.cart import Cart


@pytest.mark.django_db
def test_cart_add_new_product(request_with_session, product_factory):
    product = product_factory(initial_price=100000)
    cart = Cart(request_with_session)

    cart.add(product=product, quantity=2)

    assert len(cart) == 1
    assert cart.get_item_quantity(product=product) == 2


@pytest.mark.django_db
def test_cart_add_existing_product_increases_quantity(request_with_session, product_factory):
    product = product_factory(initial_price=200000)
    cart = Cart(request_with_session)

    cart.add(product=product)
    cart.add(product=product, quantity=3)

    assert len(cart) == 1
    assert cart.get_item_quantity(product=product) == 4


@pytest.mark.django_db
def test_cart_remove_product(request_with_session, product_factory):
    product = product_factory(initial_price=100000)
    cart = Cart(request_with_session)

    cart.add(product, quantity=3)
    assert len(cart) == 1

    cart.remove(product)
    assert len(cart) == 0


@pytest.mark.django_db
def test_cart_total_price_calculation(request_with_session, product_factory):
    p1 = product_factory(initial_price=100000)
    p2 = product_factory(initial_price=200000)
    p3 = product_factory(initial_price=150000)

    cart = Cart(request_with_session)

    cart.add(p1, quantity=2)
    assert len(cart) == 1
    assert cart.get_total_price() == 200000
    cart.add(p2, quantity=1)
    assert len(cart) == 2
    assert cart.get_total_price() == 400000
    cart.add(p3, quantity=3)
    assert len(cart) == 3
    assert cart.get_total_price() == 850000


@pytest.mark.django_db
def test_cart_iterator_contains_product_info(request_with_session, product_factory):
    product = product_factory(initial_price=1000)
    cart = Cart(request_with_session)
    cart.add(product, quantity=3)

    items = list(cart)
    first_item = items[0]

    assert first_item["product_obj"] == product
    assert first_item["quantity"] == 3
    assert first_item["item_total_price"] == 3000
