from django.db.models import Q, Sum
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views import View, generic
from products.models import Product, ProductVariant


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
        return render(request=request, template_name="core/dashboard.html")
