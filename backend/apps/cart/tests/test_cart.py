import pytest
from cart.cart import Cart, DBCartWrapper
from cart.models import Cart as DBCart
from cart.models import CartItem
from django.contrib.auth import get_user_model
from model_bakery import baker
from products.models import Product

User = get_user_model()


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


@pytest.mark.django_db
def test_db_cart_wrapper_add_limited_by_stock(client, rf):
    request = rf.get("/")
    product = baker.make(Product, stock=5)
    user = baker.make(User)
    request.user = user
    client.force_login(user)
    db_cart = baker.make(DBCart, user=user)
    baker.make(CartItem, product=product, quantity=2, cart=db_cart)
    cart_wrapper = DBCartWrapper(request)
    cart_wrapper.add(product, quantity=2)
    assert cart_wrapper.get_item_quantity(product) == 4

    cart_wrapper.add(product, quantity=4)
    assert cart_wrapper.get_item_quantity(product) == 5  # limited by stock


@pytest.mark.django_db
def test_db_cart_wrapper_decrement_limited_by_stock(client, rf):
    request = rf.get("/")
    product = baker.make(Product, stock=5)
    user = baker.make(User)
    request.user = user
    client.force_login(user)
    db_cart = baker.make(DBCart, user=user)
    baker.make(CartItem, product=product, quantity=10, cart=db_cart)
    cart_wrapper = DBCartWrapper(request)
    cart_wrapper.decrement(product)
    assert cart_wrapper.get_item_quantity(product) == 5


@pytest.mark.django_db
def test_cart_add_limited_by_stock_session(request_with_session):
    product = baker.make(Product, stock=4)
    cart = Cart(request_with_session)
    cart.add(product, quantity=3)
    assert cart.get_item_quantity(product) == 3
    cart.add(product, quantity=3)
    assert cart.get_item_quantity(product) == 4  # limited by stock


@pytest.mark.django_db
def test_cart_decrement_limited_by_stock_session(request_with_session):
    product = baker.make(Product, stock=6)
    cart = Cart(request_with_session)
    cart.add(product=product, quantity=5)
    cart.decrement(product)
    assert cart.get_item_quantity(product) == 4

    product.stock = 1
    product.save()

    cart.decrement(product)
    assert cart.get_item_quantity(product) == 1  # limited by stock
