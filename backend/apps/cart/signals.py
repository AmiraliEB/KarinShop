from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from products.models import Product

from .models import Cart, CartItem


@receiver(user_logged_in)
def merge_session_cart_to_db_cart(sender, request, user, **kwargs):
    session_cart = request.session.get("cart", {})
    if not session_cart:
        return

    try:
        db_cart, created = Cart.objects.get_or_create(user=user)

        for product_id_str, session_item_data in session_cart.items():
            product_id = int(product_id_str)
            session_quantity = session_item_data.get("quantity", 1)
            try:
                product = Product.objects.get(id=product_id)
                db_item, item_created = CartItem.objects.get_or_create(cart=db_cart, product=product)
                if item_created:
                    db_item.quantity = session_quantity
                else:
                    if (db_item.quantity + session_quantity) > product.stock:
                        db_item.quantity = product.stock
                    else:
                        db_item.quantity += session_quantity

                db_item.save()

            except Product.DoesNotExist:
                continue
        del request.session["cart"]
        request.session.modified = True

    except Exception as e:
        print(f"Error merging cart: {e}")
