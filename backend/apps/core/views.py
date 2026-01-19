from django.db.models import Count, Q
from django.shortcuts import render
from django.views import View, generic
from products.models import ProductVariant


class HomePageView(View):
    # if there are no amazing prod , del the amazing section
    slug_url_kwarg = "slug"

    def get(self, request, *args, **kwargs):
        context = {}
        amazing_products = (
            ProductVariant.objects.select_related("parent_product")
            .prefetch_related("products", "parent_product__images", "parent_product__comments")
            .filter(is_amazing=True, is_available=True)[:6]
        )
        context["amazing_products"] = amazing_products

        latest_products = ProductVariant.objects.filter(is_available=True).order_by("datetime_modified")[:6]
        context["latest_products"] = latest_products
        context["best_selling_products"] = (
            ProductVariant.objects.select_related("parent_product")
            .annotate(order_item_count=Count("orderitem", filter=Q(orderitem__order__is_paid=True)))
            .order_by("-order_item_count")[:6]
        )
        # hot_products = (
        #     ProductVariant.objects.prefetch_related()
        #     .annotate(count_cart_items=Count("cart_items"))
        #     .order_by("count_cart_items")[:15]
        # )

        # def hot_product():
        #     for product in hot_products:
        #         yield product

        context["hot_products"] = None
        context["hot_products_column"] = range(4)

        return render(request, "core/index.html", context=context)


class DashboardView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="core/dashboard.html")
