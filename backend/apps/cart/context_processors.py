from cart.cart import get_cart
from itertools import islice


def cart_context(request):
    cart = get_cart(request)
    limited_cart = list(islice(cart, 3))
    remaining_products = len(cart) - len(limited_cart)
    return {"global_cart": cart, "limited_cart": limited_cart, "remaining_products": remaining_products}
