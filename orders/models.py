from django.db import models
from products.models import Product
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from accounts.models import Address
import uuid

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = (
        ('p', _('Pending')),
        ('c', _('Confirmed')),
        ('s', _('Sent')),
        ('f', _('Finished')),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    order_number = models.CharField(max_length=20, unique=True)

    is_paid = models.BooleanField(default=False, verbose_name=_("Is Paid?"))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='p', verbose_name=_("Status"))

    address = models.ForeignKey(Address, verbose_name=_("address"), on_delete=models.SET_NULL, null=True)

    province = models.CharField(verbose_name=_("province"), max_length=50)
    city = models.CharField(verbose_name=_("city"), max_length=50)
    postal_code = models.CharField(max_length=20,verbose_name=_("postal code"))
    full_address = models.CharField(verbose_name=_("full address"), max_length=255)
    phone_number = models.CharField(max_length=20,verbose_name=_("phone number"), blank=True, null=True)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))

    def __str__(self):
        return f"Order {self.order_number} by {self.user.email}"
    
    class Meta:
        ordering = ['-datetime_created']

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = str(uuid.uuid4()).replace("-", "")[:10].upper()
        super().save(*args, **kwargs)

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())
    
    
class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=11, decimal_places=0, verbose_name=_("price (Toman)"))

    def __str__(self):
        return f"{self.quantity} x {self.product.full_name} in Order {self.order.order_number}"
    
    def get_cost(self):
        return self.price * self.quantity