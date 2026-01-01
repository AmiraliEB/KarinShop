import uuid

from accounts.models import Address
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST
from orders.models import Coupon, Order


@require_POST
def demo_gateway_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    if not user.is_authenticated:
        return render(request, "payments/failed.html", {"error": "کاربر وارد نشده است."})
    address = Address.objects.filter(user=user).first()
    if address is None:
        return render(request, "payments/failed.html", {"error": "آدرس برای کاربر یافت نشد."})
    order = Order.objects.create(
        user=user,
        province=address.province,
        city=address.city,
        postal_code=address.postal_code,
        full_address=address.full_address,
        phone_number=address.phone_number,
    )
    order = order.create_order(user=user, address=address)

    ref_id = str(uuid.uuid4().int)[:10]
    amount = order.get_total_price
    coupon_id: int | None = request.session.get("coupon_id")
    if coupon_id is not None:
        coupon = Coupon.objects.filter(id=coupon_id).first()
        if coupon is not None:
            amount, discount_amount = coupon.get_discount_amount(amount)

    context = {
        "order_id": order.order_number,
        "amount": amount,
        "ref_id": ref_id,
    }

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
