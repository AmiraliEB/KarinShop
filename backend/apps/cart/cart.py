from typing import Any, Iterator

from django.db.models import F, QuerySet
from django.http import HttpRequest
from products.models import Attribute, Product

from .models import Cart as DBCart
from .models import CartItem


class DBCartWrapper:
    def __init__(self, request: HttpRequest):
        self.request = request
        self.user = request.user
        if not self.user.is_authenticated:
            # Type Narrowing: Ensure user is a concrete 'CustomUser' model,
            return None

        self.db_cart: DBCart | None = DBCart.objects.filter(user=self.user).first()

    def __iter__(self) -> Iterator[dict]:
        if self.db_cart is None:
            return

        items: QuerySet["CartItem"] = (
            self.db_cart.items.select_related("product").prefetch_related("product__attribute_values__attribute").all()
        )

        color_attribute_obj = Attribute.objects.filter(name="رنگ").first()

        for item in items:
            color_value = "نامشخص"
            if color_attribute_obj:
                for attr_val in item.product.attribute_values.all():
                    if attr_val.attribute_id == color_attribute_obj.id:
                        color_value = attr_val.value
                        break

            yield {
                "product_obj": item.product,
                "quantity": item.quantity,
                "item_total_price": item.get_total_price(),
                "item_total_price_before_discount": item.get_total_price_before_discount(),
                "color": color_value,
            }

    def __len__(self) -> int:
        if self.db_cart is None:
            return 0
        return self.db_cart.items.count()

    def add(self, product: Product, quantity=1) -> dict[str, int]:
        cart_obj, created = DBCart.objects.get_or_create(user=self.request.user)
        cart_item_obj, cart_item_created = CartItem.objects.get_or_create(
            product=product, cart=cart_obj, defaults={"quantity": quantity}
        )
        if cart_item_created is False:
            cart_item_obj.quantity += quantity
            cart_item_obj.save()
        add_return = {
            "quantity": cart_item_obj.quantity,
            "new_item_total_price": cart_item_obj.get_total_price(),
            "item_total_price_before_discount": cart_item_obj.get_total_price_before_discount(),
        }
        return add_return

    def decrement(self, product: Product, remove=False) -> dict[str, int]:
        cart_item_obj = CartItem.objects.filter(product=product, cart=self.db_cart).first()

        base_return = {
            "quantity": 0,
            "new_item_total_price": 0,
            "item_total_price_before_discount": 0,
        }

        if not cart_item_obj or not self.db_cart:
            return base_return

        should_delete = cart_item_obj.quantity <= 1 or remove

        if not should_delete:
            cart_item_obj.quantity = F("quantity") - 1
            cart_item_obj.save()
            cart_item_obj.refresh_from_db()
            return {
                "quantity": cart_item_obj.quantity,
                "new_item_total_price": cart_item_obj.get_total_price(),
                "item_total_price_before_discount": cart_item_obj.get_total_price_before_discount(),
            }

        cart_item_obj.delete()

        return base_return

    def remove(self, product: Product) -> None:
        if self.db_cart:
            cart_item_obj = CartItem.objects.filter(product=product, cart=self.db_cart).first()
            if cart_item_obj:
                cart_item_obj.delete()

    def clear(self) -> None:
        if self.db_cart:
            self.db_cart.items.all().delete()

    def get_total_price(self) -> int:
        if self.db_cart is None:
            return 0
        return self.db_cart.get_total_price()

    def is_available(self, product: Product) -> bool:
        cart_item_obj = CartItem.objects.filter(cart=self.db_cart, product=product).first()
        if not cart_item_obj or cart_item_obj.quantity == 0:
            return False
        return True

    def get_item_quantity(self, product: Product) -> int:
        cart = self.db_cart
        cart_item_obj = CartItem.objects.filter(cart=cart, product=product).first()
        if cart_item_obj is not None:
            return cart_item_obj.quantity
        return 0


class Cart:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.session = request.session

        cart: dict | None = self.session.get("cart")
        if not cart:
            cart = self.session["cart"] = {}

        self.cart = cart

    def __iter__(self) -> Iterator[dict[str, Any]]:
        product_ids = self.cart.keys()
        products = (
            Product.objects.filter(id__in=product_ids)
            .select_related("parent_product")
            .prefetch_related("parent_product__images")
            .prefetch_related("attribute_values__attribute")
        )
        # this is necessary for prevent session serialize failure
        cart = self.cart.copy()
        color_attribute_obj = Attribute.objects.filter(name="رنگ").first()

        for product in products:
            product_id = str(product.id)

            if product_id not in cart:
                continue

            item = cart[product_id].copy()
            item["product_obj"] = product

            qty: int = item["quantity"]
            item["item_total_price"] = item["product_obj"].final_price * qty
            item["item_total_price_before_discount"] = item["product_obj"].initial_price * qty

            item["color"] = None

            if color_attribute_obj:
                for attr_val in product.attribute_values.all():
                    if attr_val.attribute_id == color_attribute_obj.id:
                        item["color"] = attr_val.value
                        break

            yield item

    def __len__(self) -> int:
        return len(self.cart.values())

    def add(self, product: Product, quantity=1) -> dict[str, int]:
        product_id = str(product.id)

        if product_id not in self.cart:
            self.cart[product_id] = {"quantity": quantity}
        else:
            self.cart[product_id]["quantity"] += quantity

        self.session.modified = True
        add_return = {
            "quantity": self.cart[product_id]["quantity"],
            "new_item_total_price": self.cart[product_id]["quantity"] * product.final_price,
            "item_total_price_before_discount": self.cart[product_id]["quantity"] * product.initial_price,
        }
        return add_return

    def decrement(self, product: Product, remove=False) -> dict[str, int]:
        product_id = str(product.id)

        if product_id in self.cart:
            if self.cart[product_id]["quantity"] <= 1 or remove is True:
                self.remove(product)
                add_return = {
                    "quantity": 0,
                    "new_item_total_price": 0,
                    "item_total_price_before_discount": 0,
                }
            else:
                self.cart[product_id]["quantity"] -= 1
                self.save()
                add_return = {
                    "quantity": self.cart[product_id]["quantity"],
                    "new_item_total_price": self.cart[product_id]["quantity"] * product.final_price,
                    "item_total_price_before_discount": self.cart[product_id]["quantity"] * product.initial_price,
                }

        return add_return

    def remove(self, product: Product) -> None:
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self) -> None:
        del self.session["cart"]
        self.save()

    def get_total_price(self) -> int:
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        return sum(product.final_price * self.cart[str(product.id)]["quantity"] for product in products)

    def is_available(self, product) -> bool:
        product_id = str(product.id)
        cart = self.cart
        try:
            product = cart[product_id]
        except KeyError:
            return False
        return True

    def get_item_quantity(self, product) -> int:
        product_id = str(product.id)
        cart = self.cart
        if self.is_available(product):
            quantity = cart[product_id]["quantity"]
            if quantity:
                return quantity
            return quantity
        return 0

    def save(self) -> None:
        self.session.modified = True


def get_cart(request: HttpRequest) -> DBCartWrapper | Cart:
    if request.user.is_authenticated:
        return DBCartWrapper(request)
    else:
        return Cart(request)
