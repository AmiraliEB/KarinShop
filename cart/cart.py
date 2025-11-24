from products.models import Product, Attribute

from .models import Cart as DBCart, CartItem
from products.models import Attribute

from django.db.models import F
class DBCartWrapper:
    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.db_cart = DBCart.objects.filter(user=self.user).first()

    def __iter__(self):
        if not self.db_cart:
            return []
        
        items = self.db_cart.items.select_related('product').all()

        for item in items:
            yield {
                'product_obj': item.product,
                'quantity': item.quantity,
                'item_total_price': item.get_total_price(),
                'color': self._get_product_color(item.product),
            }

    def __len__(self):
        if not self.db_cart:
            return 0
        return self.db_cart.items.count()

    def get_total_price(self):
        if not self.db_cart:
            return 0
        return self.db_cart.get_total_price()

    def _get_product_color(self, product):
        attribute = Attribute.objects.filter(name="رنگ")
        attr_val = product.attribute_values.filter(attribute__in=attribute).first()
        return attr_val.value if attr_val else "نامشخص"

    def add(self,product,quantity=1):
        cart_obj , created = DBCart.objects.get_or_create(user=self.request.user)
        cart_item_obj, cart_item_created = CartItem.objects.get_or_create(product=product , cart=cart_obj, defaults={'quantity':quantity})
        if not cart_item_created:
            cart_item_obj.quantity += quantity
            cart_item_obj.save()

    def remove(self, product):
        if self.db_cart:
            cart_item_obj = CartItem.objects.filter(product=product,cart=self.db_cart).first()
            if cart_item_obj:
                cart_item_obj.delete()

    def clear(self):
        if self.db_cart:
            self.db_cart.items.all().delete()

class Cart:
    def __init__(self,request):
        self.request = request
        self.session = request.session

        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}

        self.cart = cart
    
    def __iter__(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)\
                                  .select_related('parent_product')\
                                  .prefetch_related('parent_product__images')
        
        cart = self.cart.copy()

        for product in products:
            product_id = str(product.id)
            cart[product_id]['product_obj'] = product
            cart[product_id]['item_total_price'] = cart[product_id]['product_obj'].price * cart[product_id]['quantity']
            attribute = Attribute.objects.filter(name="رنگ")
            product_color = product.attribute_values.filter(attribute__in=attribute).first().value
            cart[product_id]['color'] = product_color

        for item in cart.values():
            yield item
    
    def __len__(self):
        return len(self.cart.values())

    def add(self,product,quantity=1):
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {'quantity':quantity}
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def remove(self,product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        del self.session['cart']

    def get_total_price(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        return sum(product.price * self.cart[str(product.id)]['quantity'] for product in products)
        

    def save(self):
        self.session.modified = True


def get_cart(request):
    if request.user.is_authenticated:
        return DBCartWrapper(request)
    else:
        return Cart(request)