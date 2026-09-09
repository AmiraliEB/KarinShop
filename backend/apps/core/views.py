from accounts.models import Address, Profile
from django.db.models import OuterRef, Prefetch, Q, Subquery, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View, generic
from orders.models import Order, OrderItem
from products.models import ProductVariant


class HomePageView(View):
    # if there are no amazing prod , del the amazing section
    slug_url_kwarg = "slug"

    def get(self, request, *args, **kwargs):
        context = {}
        product_variant = ProductVariant.objects.filter(is_available=True)
        amazing_product_variants = (
            ProductVariant.objects.select_related("parent_product")
            .prefetch_related("products", "parent_product__images", "parent_product__comments")
            .filter(is_amazing=True, is_available=True)[:6]
        )
        context["amazing_product_variants"] = amazing_product_variants

        latest_product_variants = product_variant.order_by("datetime_modified")[:6]
        context["latest_product_variants"] = latest_product_variants
        best_selling = product_variant.annotate(
            paid_items_count=Coalesce(
                Sum("products__order_items__quantity", filter=Q(products__order_items__order__is_paid=True)), 0
            )
        )
        context["best_selling_product_variants"] = best_selling.order_by("paid_items_count")
        context["hot_product_variants"] = None
        context["hot_product_variants_column"] = range(4)

        return render(request, "core/index.html", context=context)


class DashboardView(generic.View):
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.profile
        except (AttributeError, Profile.DoesNotExist):
            return redirect(reverse("account_login"))
        user_orders = user.orders.order_by("-datetime_created").prefetch_related(
            Prefetch("items", queryset=OrderItem.objects.select_related("product__product_variant"))
        )
        user_addresses_count = user.addresses.count()

        context = {
            "user_profile": profile,
            "user_obj": user,
            "user_orders": user_orders[:3],
            "user_orders_count": user_orders.count(),
            "user_addresses_count": user_addresses_count,
        }
        return render(request=request, template_name="core/dashboard.html", context=context)


class AboutPageView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="core/about.html")


class ContactPageView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="core/contact-us.html")


class QuestionPageView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="core/questions.html")
