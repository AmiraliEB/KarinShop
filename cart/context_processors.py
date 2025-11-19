from cart.cart import Cart , DBCartWrapper
from cart.models import Cart as DBCart
from products.models import Attribute
def cart_context(request):
    if request.user.is_authenticated:
        cart = DBCartWrapper(request)        
    else:
        cart = Cart(request)
    return {'global_cart':cart}