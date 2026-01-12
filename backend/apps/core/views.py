from django.shortcuts import render
from django.views import View
from products.models import Product


class HomePageView(View):
    # if there are no amazing prod , del the amazing section
    slug_url_kwarg = "slug"

    def get(self, request, *args, **kwargs):
        context = {}
        amazing_products = (
            Product.objects.select_related("parent_product")
            .prefetch_related("parent_product__images", "parent_product__comments")
            .filter(is_amazing=True)[:6]
        )
        context["amazing_products"] = amazing_products

        latest_products = Product.objects.order_by("datetime_modified")[:6]
        context["latest_products"] = latest_products

        return render(request, "core/index.html", context=context)
