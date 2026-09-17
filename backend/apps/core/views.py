from accounts.models import Address, Profile
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Prefetch, Q, Sum, prefetch_related_objects
from django.db.models.functions import Coalesce
from django.shortcuts import render
from django.views import View, generic
from orders.models import OrderItem
from products.models import Product, ProductImage, ProductVariant


class HomePageView(View):
    slug_url_kwarg = "slug"

    def get(self, request, *args, **kwargs):
        base_qs = (
            ProductVariant.objects.filter(is_available=True)
            .select_related("parent_product")
            .annotate(
                rating_avg=Coalesce(
                    Avg(
                        "parent_product__comments__rating",
                        filter=Q(parent_product__comments__is_approved=True),
                    ),
                    0.0,
                )
            )
        )
        amazing_variants = list(base_qs.filter(is_amazing=True)[:6])
        latest_variants = list(base_qs.order_by("-datetime_modified")[:6])
        best_selling_variants = list(
            base_qs.annotate(
                paid_items_count=Coalesce(
                    Sum(
                        "products__order_items__quantity",
                        filter=Q(products__order_items__order__is_paid=True),
                    ),
                    0,
                )
            ).order_by("-paid_items_count")[:6]
        )

        all_variants = amazing_variants + latest_variants + best_selling_variants

        prefetch_related_objects(
            all_variants,
            Prefetch("products", queryset=Product.objects.filter(is_available=True)),
            Prefetch("parent_product__images", queryset=ProductImage.objects.all()),
        )

        context = {
            "amazing_product_variants": amazing_variants,
            "latest_product_variants": latest_variants,
            "best_selling_product_variants": best_selling_variants,
            "hot_product_variants": None,
            "hot_product_variants_column": range(4),
        }

        return render(request, "core/index.html", context=context)


class DashboardView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.profile
        except (AttributeError, Profile.DoesNotExist):
            profile = None

        user_orders = user.orders.order_by("-datetime_created").prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product__product_variant__parent_product").prefetch_related(
                    Prefetch(
                        "product__product_variant__parent_product__images",
                        queryset=ProductImage.objects.filter(is_main_image=True),
                    )
                ),
            )
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


class DashboardAddressView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        user = request.user
        address = Address.objects.filter(user=user).first()
        try:
            profile = user.profile
        except (AttributeError, Profile.DoesNotExist):
            profile = None
        context = {
            "user_obj": user,
            "user_addresses_obj": address,
            "user_profile": profile,
        }
        return render(request=request, template_name="core/dashboard-address.html", context=context)


class DashboardMessagesView(LoginRequiredMixin, generic.View):
    def get(self, request, *args, **kwargs):
        user = request.user
        try:
            profile = user.profile
        except (AttributeError, Profile.DoesNotExist):
            profile = None

        context = {
            "user_obj": user,
            "user_profile": profile,
        }
        return render(request=request, template_name="core/dashboard-messages.html", context=context)


class AboutPageView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="core/about.html")


class ContactPageView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="core/contact-us.html")


class QuestionPageView(generic.View):
    def get(self, request, *args, **kwargs):
        return render(request=request, template_name="core/questions.html")
