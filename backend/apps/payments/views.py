import uuid
from datetime import datetime
from typing import Any

from cart.cart import get_cart
from django.core.exceptions import BadRequest
from django.db import transaction
from django.db.models import BooleanField, Case, F, QuerySet, Value, When
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

<<<<<<< HEAD
from orders.models import Coupon, Order, OrderItem
from products.models import Product

=======
from orders.models import Coupon, Order

>>>>>>> 667098c (fix: in payment replace name product to product_variant in both context name and template var)


def demo_gateway_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        # TODO: add an already paid page too
        amount = 0
        ref_id = str(uuid.uuid4().int)[:10]
        order_number = request.GET.get("order_number")
        user = request.user
        if not user.is_authenticated:
            return render(
                request,
                "payments/failed-payment.html",
                {"order_number": order_number, "amount": amount, "ref_id": ref_id},
            )
        order = Order.objects.filter(order_number=order_number, user=user).first()
        if order is None:
            raise BadRequest("400 Bad Request")
        coupon_id = request.session.get("coupon_id")
        amount = order.get_total_price
        if coupon_id is not None:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon is not None:
                amount, discount_amount = coupon.get_discount_amount(amount)

        context = {"order_number": order_number, "amount": amount, "ref_id": ref_id}
    return render(request, "payments/demo_gateway.html", context=context)


@require_POST
def payment_verify_view(request: HttpRequest) -> HttpResponse:
    context: dict[str, Any] = {"ref_id": request.POST.get("ref_id"), "amount": request.POST.get("amount")}
    order_number = request.POST.get("order_number")
    context["date_now"] = datetime.now()
    error_template = "payments/failed-payment.html"

    if "success" in request.POST:
        if not order_number:
            context["error"] = "شماره سفارش یافت نشد"
            return render(request, error_template, context)
        if order_number is not None:
            order = Order.objects.filter(order_number=order_number).first()
            if order is not None and order.status == "failed":
                context["error"] = "این سفارش قبلا ناموفق بوده است, مبلغ به حساب شما بازمی‌گردد"
                return render(request, error_template, context)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().filter(order_number=order_number).first()

                if order is None or order.is_paid:
                    context["error"] = "این سفارش قبلاً پرداخت شده یا وجود ندارد, مبلغ به حساب شما بازمی‌گردد"
                    return render(request, error_template, context)

                coupon_id = request.session.get("coupon_id")
                if coupon_id:
                    coupon = Coupon.objects.select_for_update().filter(id=coupon_id).first()
                    if coupon is not None:
                        if coupon.is_usable:
                            coupon.used_count = F("used_count") + 1
                            coupon.save(update_fields=["used_count"])
                        del request.session["coupon_id"]

                order_items: QuerySet[OrderItem] = order.items.select_related("product").all()

                for order_item in order_items:
                    product: Product = order_item.product
                    if product.stock < order_item.quantity:
                        transaction.set_rollback(True)
                        context["error"] = f"محصول {product} به اندازه کافی در انبار موجود نیست."
                        return render(request, error_template, context)
                    Product.objects.filter(id=product.id).update(
                        stock=F("stock") - order_item.quantity,
                        is_available=Case(
                            When(stock__gt=order_item.quantity, then=Value(True)),
                            default=Value(False),
                            output_field=BooleanField(),
                        ),
                    ),

                order.is_paid = True
                order.status = "c"
                order.save()

                cart = get_cart(request)
                cart.clear()

            return render(request, "payments/successful-payment.html", context=context)

        except Exception as e:
            print(f"Payment Error: {e}")
            context["error"] = "خطایی در ثبت نهایی سفارش رخ داد. مبلغ به حساب شما بازمی‌گردد."
            order = Order.objects.filter(order_number=order_number).first()
            if order is not None and order.status != "failed":
                order.is_paid = True
                order.status = "failed"
                order.save()
            return render(request, error_template, context)

    elif "failure" in request.POST:
        context["error"] = "پرداخت ناموفق بود."
        return render(request, error_template, context)

    elif "cancel" in request.POST:
        context["error"] = "پرداخت توسط کاربر لغو شد"
        return render(request, error_template, context)

    context["error"] = "خطای ناشناخته رخ داد"
    return render(request, error_template, context)
