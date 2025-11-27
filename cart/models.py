from django.db import models
from django.db.models import F, Sum
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def get_total_price(self):      
        result = self.items.aggregate(
            total=Sum(F('quantity') * F('product__final_price'))
        )
        return result['total'] or 0
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_("cart"), on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', verbose_name=_("product"), on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name=_("quantity"), default=1)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))
    
    def __str__(self):
        return f"{self.quantity} عدد از {self.product.parent_product.name} در سبد {self.cart.user.username}"
    
    def get_total_price(self): 
        price = self.product.final_price
        return price * self.quantity