from cart.cart import get_cart
def cart_context(request):
    cart = get_cart(request)
    return {'global_cart':cart}