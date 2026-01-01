import nanoid
from accounts.models import Address
from cart.models import Cart, CartItem
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _
from products.models import Product

User = get_user_model()


class Order(models.Model):
    STATUS_CHOICES = (
        ("p", _("Pending")),
        ("c", _("Confirmed")),
        ("s", _("Sent")),
        ("f", _("Finished")),
    )

    SHIPPING_CHOICES = (
        ("post", _("Post")),
        ("tipax", _("Tipax")),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    order_number = models.CharField(max_length=20, unique=True)

    is_paid = models.BooleanField(default=False, verbose_name=_("Is Paid?"))
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="p", verbose_name=_("Status"))

    province = models.CharField(verbose_name=_("province"), max_length=50)
    city = models.CharField(verbose_name=_("city"), max_length=50)
    postal_code = models.CharField(max_length=20, verbose_name=_("postal code"))
    full_address = models.CharField(verbose_name=_("full address"), max_length=255)
    phone_number = models.CharField(max_length=20, verbose_name=_("phone number"), blank=True, null=True)

    shipping_method = models.CharField(
        max_length=10, choices=SHIPPING_CHOICES, default="post", verbose_name=_("shipping method")
    )

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))

    def __str__(self):
        return f"Order {self.order_number} by {self.user.email}"

    class Meta:
        ordering = ["-datetime_created"]

    def save(self, *args, **kwargs):
        if not self.order_number:
            alphabet = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"
            raw_code = nanoid.generate(alphabet=alphabet, size=10)
            self.order_number = f"{raw_code[:3]}-{raw_code[3:6]}-{raw_code[6:]}"

        super().save(*args, **kwargs)

    @property
    def get_total_price(self) -> int:
        return sum(item.get_cost() for item in self.items.all())

    def create_order(self, user, address: Address | None, is_paid=False, status="p") -> "Order":
        if address is None:
            return self
        self.is_paid = is_paid
        self.status = status
        self.save()
        self.create_order_items_from_cart(cart=Cart.objects.filter(user=user).first())
        return self

    def create_order_items_from_cart(self, cart: Cart | None):
        if cart is None:
            return
        cart_items: QuerySet[CartItem] = cart.items.all()
        for item in cart_items:
            product: Product = item.product
            if product.final_price is not None:
                OrderItem.objects.create(
                    order=self,
                    product=product,
                    quantity=item.quantity,
                    price=product.final_price,
                )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=11, decimal_places=0, verbose_name=_("price (Toman)"))

    def __str__(self):
        return f"{self.quantity} x {self.product.full_name} in Order {self.order.order_number}"

    def get_cost(self):
        return self.price * self.quantity


class Coupon(models.Model):
    discount_type_choices = (
        ("v", _("Fixed Amount")),
        ("p", _("Percentage")),
    )
    code = models.CharField(max_length=50, unique=True, verbose_name=_("Coupon Code"))
    discount_value = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_("Discount Value"))
    discount_type = models.CharField(max_length=1, choices=discount_type_choices, verbose_name=_("Discount Type"))

    quantity = models.PositiveIntegerField(verbose_name=_("Available Quantity"), default=1)
    used_count = models.PositiveIntegerField(default=0, verbose_name=_("Used Count"))
    active = models.BooleanField(default=True, verbose_name=_("Is Active"))

    valid_from = models.DateTimeField(verbose_name=_("Valid From"))
    valid_to = models.DateTimeField(verbose_name=_("Valid To"))

    def __str__(self):
        return self.code

    def clean(self):
        if self.discount_type == "p" and self.discount_value > 100:
            raise ValidationError({"discount_value": _("Percentage discount cannot be more than 100.")})

        if self.valid_to and self.valid_from and self.valid_to < self.valid_from:
            raise ValidationError({"valid_to": _("End date cannot be before start date.")})

    def get_discount_amount(self, total_price: int) -> tuple[int, int]:
        discount_amount = 0
        if self.discount_type == "p":
            discount_amount = int(total_price * (self.discount_value / 100))
        elif self.discount_type == "v":
            discount_amount = int(self.discount_value)

        if discount_amount > total_price:
            discount_amount = total_price
        total_price -= discount_amount
        return total_price, discount_amount

    @property
    def calculate_total_price(self, total_price: int) -> int:
        if self.discount_type == "p":
            discount_amount = total_price * (self.discount_value / 100)
        elif self.discount_type == "v":
            discount_amount = self.discount_value

        if discount_amount > total_price:
            discount_amount = total_price
        total_price -= discount_amount
        return total_price

    @property
    def is_usable(self):
        from django.utils import timezone

        now = timezone.now()
        return self.active and self.valid_from <= now <= self.valid_to and self.used_count < self.quantity
