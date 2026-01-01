import uuid

from accounts.models import Address
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from orders.models import Coupon, Order


def demo_gateway_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        amount = 0
        ref_id = str(uuid.uuid4().int)[:10]
        order_number = request.GET.get("order_number")
        context = {"order_number": order_number, "amount": amount, "ref_id": ref_id}
        user = request.user
        if not user.is_authenticated:
            return render(request, "payments/failed-payment.html", context=context)
        order = Order.objects.filter(order_number=order_number, user=user).first()
        if order is None:
            return render(request, "payments/failed-payment.html", context=context)
        coupon_id = request.session.get("coupon_id")
        amount = order.get_total_price
        if coupon_id is not None:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon is not None:
                amount, discount_amount = coupon.get_discount_amount(amount)

    return render(request, "payments/demo_gateway.html", context=context)


@require_POST
def payment_verify_view(request: HttpRequest) -> HttpResponse:

    context = {"ref_id": request.POST.get("ref_id"), "amount": request.POST.get("amount")}
    if "success" in request.POST:
        return render(request, "payments/successful-payment.html", context=context)
    elif "failure" in request.POST:
        context["error"] = "پرداخت ناموفق بود."
        return render(request, "payments/failed-payment.html", context=context)
    elif "cancel" in request.POST:
        context["error"] = "پرداخت توسط کاربر لغو شد"
        return render(request, "payments/failed-payment.html", context=context)
    context["error"] = "خطای ناشناخته رخ داد"
    return render(request, "payments/failed-payment.html", context=context)
