from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _
from products.models import ProductVariant

User = get_user_model()


class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name=_("user"), on_delete=models.CASCADE)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def get_cart_total_price(self):
        result = self.items.aggregate(total=Sum(F("quantity") * F("product__final_price")))
        return result["total"] or 0


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, verbose_name=_("cart"), on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        ProductVariant, verbose_name=_("product"), on_delete=models.CASCADE, related_name="cart_items"
    )
    quantity = models.PositiveIntegerField(verbose_name=_("quantity"), default=1)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def __str__(self):
        return f"{self.quantity} عدد از {self.product.product_variant.parent_product.name} در سبد {self.cart.user.username}"

    def get_item_total_price(self):
        price = self.product.final_price
        return price * self.quantity

    def get_total_price_before_discount(self):
        if self.product.has_discount():
            price = self.product.initial_price
            return price * self.quantity
        return None
