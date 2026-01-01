import uuid

from accounts.models import Address
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_POST
from orders.models import Order


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
    context = {
        "order_id": order.order_number,
        "amount": order.get_total_price(),
        "ref_id": ref_id,
    }

    base_url = reverse("demo-gateway")
    params = f"?order_number={order.order_number}&amount={order.get_total_price()}"
    context["payment_url"] = f"{base_url}{params}"

    return render(request, "payments/demo_gateway.html", context=context)


def payment_verify_view(request):
    status = request.GET.get("status")
    order_id = request.GET.get("order_id")
    ref_id = request.GET.get("ref_id")

    if status == "success":
        return render(request, "payments/success.html", {"ref_id": ref_id})
    else:
        return render(request, "payments/failed.html", {"error": "پرداخت توسط کاربر لغو شد یا ناموفق بود."})
