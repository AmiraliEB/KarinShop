import uuid

from cart.cart import get_cart
from django.core.exceptions import BadRequest
from django.db import IntegrityError, transaction
from django.db.models import F
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from orders.models import Coupon, Order, OrderItem
from products.models import Product


def demo_gateway_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        amount = 0
        ref_id = str(uuid.uuid4().int)[:10]
        order_number = request.GET.get("order_number")
        # TODO:order should be for requesting user
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
    context = {"ref_id": request.POST.get("ref_id"), "amount": request.POST.get("amount")}
    order_number = request.POST.get("order_number")

    error_template = "payments/failed-payment.html"

    if "success" in request.POST:
        if not order_number:
            context["error"] = "شماره سفارش یافت نشد"
            return render(request, error_template, context)

        try:
            with transaction.atomic():
                order = Order.objects.select_for_update().filter(order_number=order_number).first()

                if order is None or order.is_paid:
                    context["error"] = "این سفارش قبلاً پرداخت شده یا وجود ندارد."
                    return render(request, error_template, context)

                coupon_id = request.session.get("coupon_id")
                if coupon_id:
                    coupon = Coupon.objects.select_for_update().filter(id=coupon_id).first()
                    if coupon is not None:
                        if coupon.is_usable:
                            coupon.used_count = F("used_count") + 1
                            coupon.save(update_fields=["used_count"])
                        del request.session["coupon_id"]

                items = order.items.select_related("product").all()
                for item in items:
                    product: Product = item.product
                    product.stock = F("stock") - item.quantity
                    product.save(update_fields=["stock"])

                order.is_paid = True
                order.status = "c"
                order.save(update_fields=["is_paid", "status"])

                cart = get_cart(request)
                cart.clear()

            return render(request, "payments/successful-payment.html", context=context)

        except Exception as e:
            print(f"Payment Error: {e}")
            context["error"] = "خطایی در ثبت نهایی سفارش رخ داد. مبلغ به حساب شما بازمی‌گردد."
            return render(request, error_template, context)

    elif "failure" in request.POST:
        context["error"] = "پرداخت ناموفق بود."
        return render(request, error_template, context)

    elif "cancel" in request.POST:
        context["error"] = "پرداخت توسط کاربر لغو شد"
        return render(request, error_template, context)

    context["error"] = "خطای ناشناخته رخ داد"
    return render(request, error_template, context)
