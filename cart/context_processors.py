from cart.cart import Cart
def cart_context(request):
    cart = Cart(request)
    return {'global_cart':cart}