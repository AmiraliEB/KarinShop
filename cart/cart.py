from products.models import Product

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

    