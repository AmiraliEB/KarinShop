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
                'item_total_price_before_discount': item.get_total_price_before_discount(),
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
        add_return= {
            'quantity':cart_item_obj.quantity,
            'new_item_total_price':cart_item_obj.get_total_price(),
            'item_total_price_before_discount':cart_item_obj.get_total_price_before_discount(),
        }
        return add_return

    def decrement(self,product):
        cart_item_obj = CartItem.objects.filter(product=product,cart=self.db_cart).first()
        if self.db_cart and cart_item_obj:
            if cart_item_obj.quantity > 1:
                cart_item_obj.quantity = F('quantity') - 1
                cart_item_obj.save()
                cart_item_obj.refresh_from_db()
            else:
                cart_item_obj.delete()
        
        decrement_return = {
            'quantity':cart_item_obj.quantity,
            'new_item_total_price':cart_item_obj.get_total_price(),
            'item_total_price_before_discount':cart_item_obj.get_total_price_before_discount(),
        }
        return decrement_return

    def remove(self, product):
        if self.db_cart:
            cart_item_obj = CartItem.objects.filter(product=product,cart=self.db_cart).first()
            if cart_item_obj:
                cart_item_obj.delete()

    def clear(self):
        if self.db_cart:
            self.db_cart.items.all().delete()

    def is_available(self,product):
        cart_item_obj = CartItem.objects.filter(cart=self.db_cart,product=product).first()
        if not cart_item_obj or cart_item_obj.quantity == 0:
            return False
        return True
    
    def get_item_quantity(self, product):
        cart = self.db_cart
        cart_item_obj = CartItem.objects.filter(cart=cart,product=product).first()
        if cart_item_obj:
            return cart_item_obj.quantity
        return 0

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

            # this is necessary for prevent session serialize failure  
            item = cart[product_id].copy()

            item['product_obj'] = product
            item['item_total_price'] = item['product_obj'].final_price * cart[product_id]['quantity']
            item['item_total_price_before_discount'] = item['product_obj'].initial_price * cart[product_id]['quantity']
            attribute = Attribute.objects.filter(name="رنگ")
            color_attr = product.attribute_values.filter(attribute__in=attribute).first()

            item['color'] = color_attr.value if color_attr else None

            cart[product_id] = item
        
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

        self.session.modified = True
        add_return = {
            'quantity': self.cart[product_id]['quantity'],
            'new_item_total_price': self.cart[product_id]['quantity'] * product.final_price,
            'item_total_price_before_discount': self.cart[product_id]['quantity'] * product.initial_price,
        }
        return add_return

    def decrement(self,product):
        product_id = str(product.id)

        if product_id in self.cart:
            if self.cart[product_id]['quantity'] > 1:
                self.cart[product_id]['quantity'] -= 1
                self.save()
                add_return = {
                    'quantity': self.cart[product_id]['quantity'],
                    'new_item_total_price': self.cart[product_id]['quantity'] * product.final_price,
                    'item_total_price_before_discount': self.cart[product_id]['quantity'] * product.initial_price,
                }
            else:
                self.remove(product)
                add_return = {
                    'quantity': 0,
                    'new_item_total_price': 0,
                    'item_total_price_before_discount': 0,
                }


        return add_return

    def remove(self,product):
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        del self.session['cart']
        self.save()

    def get_total_price(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)
        
        return sum(product.final_price * self.cart[str(product.id)]['quantity'] for product in products)

    def save(self):
        self.session.modified = True

    def is_available(self,product):
        product_id = str(product.id)
        cart = self.cart
        try:
            product = cart[product_id]
        except KeyError:
            return False
        return True
    
    def get_item_quantity(self, product):
        product_id = str(product.id)
        cart = self.cart
        if self.is_available(product):
            quantity = cart[product_id]['quantity']
            print(quantity)
            if quantity:
                return quantity
            return quantity
        return 0
    
def get_cart(request):
    if request.user.is_authenticated:
        return DBCartWrapper(request)
    else:
        return Cart(request)