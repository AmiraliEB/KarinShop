import uuid

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def demo_gateway_view(request: HttpRequest) -> HttpResponse:
    order_id = request.GET.get("order_id")
    amount = request.GET.get("amount")

    ref_id = str(uuid.uuid4().int)[:10]

    context = {
        "order_id": order_id,
        "amount": amount,
        "ref_id": ref_id,
    }
    return render(request, "payments/demo_gateway.html", context)


def payment_verify_view(request):
    status = request.GET.get("status")
    order_id = request.GET.get("order_id")
    ref_id = request.GET.get("ref_id")

    if status == "success":
        return render(request, "payments/success.html", {"ref_id": ref_id})
    else:
        return render(request, "payments/failed.html", {"error": "پرداخت توسط کاربر لغو شد یا ناموفق بود."})
