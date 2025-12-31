from datetime import timedelta

from accounts.models import Address, Profile
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST
from django.views.generic import View
from orders.models import Coupon
from products.models import Product

from .cart import get_cart
from .forms import CartAddAddressFrom, CouponApplyForm
from .models import Cart


def refresh_shortcut():
    response = HttpResponse("home")
    response["HX-Refresh"] = "true"
    return response


class CartView(View):
    def get(self, request, *args, **kwargs):
        cart = get_cart(request)
        product_obj = []

        for cart_item in cart:
            product_obj.append(cart_item.get("product_obj"))

        paginator = Paginator(product_obj, 4)
        page_number = self.request.GET.get("page")
        if not page_number:
            page_number = 1
        paginator_page = paginator.page(page_number)
        page_objects = paginator_page.object_list

        context = {
            "page_objects": page_objects,
            "paginator": paginator,
            "paginator_page": paginator_page,
        }

        return render(request, "cart/cart.html", context)


today = timezone.localdate()
time_to_leave_warehouse = today + timedelta(days=2)


class CheckoutView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user).first()
        if not cart.items.first():
            messages.error(request, _("Your cart is empty."))
            return redirect("cart_detail")
        form = CartAddAddressFrom()

        # this is default coupon for payment page
        # if dont want it, just remove this block
        coupon = Coupon.objects.filter(code__iexact="DEMO_MODE").first()
        request.session["coupon_id"] = coupon.id
        address = Address.objects.filter(user=request.user).first()

        return render(
            request,
            "cart/checkout.html",
            {"form": form, "time_to_leave_warehouse": time_to_leave_warehouse, "address": address},
        )

    def post(self, request, *args, **kwargs):
        form = CartAddAddressFrom(request.POST)
        current_user = request.user
        profile, created = Profile.objects.get_or_create(user=current_user)

        if form.is_valid():
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]

            province = form.cleaned_data["province"]
            city = form.cleaned_data["city"]
            postal_code = form.cleaned_data["postal_code"]
            full_address = form.cleaned_data["full_address"]
            phone_number = form.cleaned_data["phone_number"]

            profile.user = request.user
            profile.first_name = first_name
            profile.last_name = last_name
            profile.save()

            new_address = Address()
            new_address.user = request.user
            new_address.province = province
            new_address.city = city
            new_address.postal_code = postal_code
            new_address.full_address = full_address
            new_address.phone_number = phone_number
            new_address.save()

            return redirect("payment")
        else:
            return render(
                request, "cart/checkout.html", {"form": form, "time_to_leave_warehouse": time_to_leave_warehouse}
            )


class PaymentView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):

        address = Address.objects.filter(user=request.user).first()
        if not address:
            messages.error(request, _("Please add a shipping address first."))
            return redirect("checkout")
        cart = Cart.objects.filter(user=request.user).first()
        if not cart.items.first():
            messages.error(request, _("Your cart is empty."))
            return redirect("cart_detail")
        total_price = cart.get_total_price()

        coupon_id = request.session.get("coupon_id")
        coupon = None
        discount_amount = 0

        if coupon_id:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if coupon and coupon.is_usable:
                if coupon.discount_type == "p":
                    discount_amount = total_price * (coupon.discount_value / 100)
                elif coupon.discount_type == "v":
                    discount_amount = coupon.discount_value

                if discount_amount > total_price:
                    discount_amount = total_price

                total_price -= discount_amount
            else:
                del request.session["coupon_id"]
                coupon = None

        context = {
            "coupon_form": CouponApplyForm(),
            "time_to_leave_warehouse": time_to_leave_warehouse,
            "total_price": int(total_price),
            "discount_amount": int(discount_amount),
            "coupon": coupon,
            "address_obj": address,
        }
        return render(request, template_name="cart/payment.html", context=context)

    def post(self, request, *args, **kwargs):
        coupon = None
        total_price = Cart.objects.get(user=request.user).get_total_price()
        address = Address.objects.filter(user=request.user).first()
        discount_amount = 0
        if not address:
            messages.error(request, _("Please add a shipping address first."))
            return redirect("checkout")

        cart = Cart.objects.filter(user=request.user).first()
        if not cart:
            messages.error(request, _("Your cart is empty."))
            return redirect("cart_detail")
        total_price = cart.get_total_price()

        return render(
            request,
            template_name="cart/payment.html",
            context={
                "coupon_form": CouponApplyForm(),
                "time_to_leave_warehouse": time_to_leave_warehouse,
                "total_price": total_price,
                "address_obj": address,
                "discount_amount": int(discount_amount),
                "coupon": coupon,
            },
        )


@require_POST
def remove_coupon(request):
    if "coupon_id" in request.session:
        del request.session["coupon_id"]

    if request.htmx:
        total_price = Cart.objects.get(user=request.user).get_total_price()
        context = {"coupon_form": CouponApplyForm(), "coupon": None, "total_price": total_price}
        return render(request, "cart/partials/coupon_area.html", context=context)
    return redirect("payment")


@require_POST
def apply_coupon(request):
    if request.htmx:
        coupon_form = CouponApplyForm(request.POST)
        total_price = Cart.objects.get(user=request.user).get_total_price()
        if coupon_form.is_valid():
            coupon_code = coupon_form.cleaned_data["code"]
            try:
                coupon = Coupon.objects.get(code__iexact=coupon_code)
                if coupon.is_usable:
                    request.session["coupon_id"] = coupon.id
                    if coupon.discount_type == "p":
                        discount_amount = total_price * (coupon.discount_value / 100)
                    elif coupon.discount_type == "v":
                        discount_amount = coupon.discount_value

                    if discount_amount > total_price:
                        discount_amount = total_price

                    total_price -= discount_amount
                    return render(
                        request,
                        "cart/partials/coupon_area.html",
                        {"coupon": coupon, "discount_amount": discount_amount, "total_price": total_price},
                    )
                else:
                    request.session["coupon_id"] = None
                    coupon_form.add_error("code", _("This discount code is invalid or cannot be applied."))
                    coupon = None
            except Coupon.DoesNotExist:
                coupon_form.add_error("code", _("Discount code not found."))
            context = {
                "coupon_form": coupon_form,
                "total_price": total_price,
            }
            return render(request, "cart/partials/coupon_area.html", context=context)
        return render(
            request, "cart/partials/coupon_area.html", {"coupon_form": coupon_form, "total_price": total_price}
        )
    return redirect("payment")


@require_POST
def clear_items_form_cart(request):
    if request.htmx:
        cart = get_cart(request)
        cart.clear()
        return render(request, "cart/partials/clear_items_in_cart.html")
    return redirect("cart_detail")


@require_POST
def update_cart_item(request, action, pk):
    cart = get_cart(request)
    product_obj = get_object_or_404(Product, pk=pk)

    if action == "add":
        action_return = cart.add(product_obj)
    elif action == "remove":
        action_return = cart.decrement(product_obj, True)
    elif action == "decrement":
        action_return = cart.decrement(product_obj)

    quantity = action_return.get("quantity")
    item_total_price = action_return.get("new_item_total_price")
    is_product_available = cart.is_available(product_obj)

    cart_item = {
        "product_obj": product_obj,
        "quantity": quantity,
        "item_total_price": item_total_price,
        "product_available_in_cart": is_product_available,
        "item_total_price_before_discount": action_return.get("item_total_price_before_discount"),
    }

    context = {
        "cart_item": cart_item,
        "product_obj": product_obj,
        "product_available_in_cart": is_product_available,
        "item_quantity": quantity,
        "product": product_obj,
        "item_total_price": item_total_price,
    }

    return render(request, "cart/partials/cart_update_response.html", context)
