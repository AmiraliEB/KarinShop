from datetime import timedelta

from cart.cart import get_cart
from cart.forms import CartAddProductForm
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import DetailView, View
from products.models import AttributeValue, Comments, Product, ProductParent, ProductVariant

from .filters import ProductFilter
from .forms import CommentForm


def post_redirect_view(request, pk):
    product_obj = get_object_or_404(ProductVariant, pk=pk)
    return redirect(
        "products:product_detail",
        pk=product_obj.pk,
        slug=slugify(product_obj.full_name, allow_unicode=True),
        permanent=True,
    )


class ProductDetailView(DetailView):
    model = ProductVariant
    template_name = "products/product_details.html"
    context_object_name = "product_variant"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object: ProductVariant = self.get_object()
        if "comment_submit" in request.POST:
            return self.process_comment(request)

        if "cart_submit" in request.POST:
            return self.process_cart(request)

        return redirect(self.object.get_absolute_url())

    def process_comment(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            messages.warning(request, "برای ثبت دیدگاه، لطفا ابتدا وارد شوید.")
            return redirect(f"{settings.LOGIN_URL}?next={self.object.get_absolute_url()}")

        comment_form = CommentForm(request.POST)

        if comment_form.is_valid():
            comment_form.save(request, product=self.object)

            messages.success(request, "دیدگاه شما با موفقیت ثبت شد و پس از تایید نمایش داده می‌شود.")
            return redirect(self.object.get_absolute_url())
        else:
            context = self.get_context_data(comment_form=comment_form)
            return self.render_to_response(context)

    def process_cart(self, request: HttpRequest) -> HttpResponse:
        cart_form = CartAddProductForm(request.POST)
        if cart_form.is_valid():
            cart = get_cart(request)
            cart.add(self.object, cart_form.cleaned_data["quantity"])
            messages.success(request, "محصول با موفقیت به سبد خرید اضافه شد.")
            return redirect(self.object.get_absolute_url())
        else:
            context = self.get_context_data(cart_form=cart_form)
            return self.render_to_response(context)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            "parent_product__brand", "parent_product__category", "parent_product"
        ).prefetch_related(
            Prefetch(
                "parent_product__specification_values",
                queryset=AttributeValue.objects.select_related("attribute__attribute_category").order_by(
                    "attribute__attribute_category__sort_order"
                ),
                to_attr="sorted_attribute_values",
            ),
            "parent_product__images",
            "parent_product__comments",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = get_cart(self.request)

        product_variant = self.object

        comments = (
            Comments.objects.filter(parent_product=product_variant.parent_product, is_approved=True)
            .select_related("user")
            .order_by("-datetime_created")
        )
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get("page")
        comments_filter_by_page_number = paginator.get_page(page_number)

        context["discount_percentage"] = product_variant.discount_percentage
        context["grouped_attributes"] = product_variant.parent_product.grouped_specifications

        context["comments"] = comments_filter_by_page_number
        context["comments_count"] = product_variant.parent_product.get_comment_count(comments)
        context["average_rating"] = product_variant.parent_product.get_average_rate(comments)

        context["album_images"] = product_variant.parent_product.images.filter(is_main_image=False)

        if "comment_form" not in context:
            context["comment_form"] = CommentForm()
        if "cart_form" not in context:
            context["cart_form"] = CartAddProductForm()

        category = product_variant.parent_product.category
        brand = product_variant.parent_product.brand

        # TODO: related parent should calculate in model
        # TODO: related products should be available
        related_parent = (
            ProductParent.objects.filter(category=category, brand=brand)
            .exclude(id=product_variant.parent_product.id)
            .distinct()[:6]
        )
        if not related_parent:
            related_parent = (
                ProductParent.objects.filter(category=category)
                .exclude(id=product_variant.parent_product.id)
                .distinct()[:6]
            )
        context["related_products"] = []
        for parent_obj in related_parent:
            if parent_obj.product_variants.first() is None:
                continue
            context["related_products"].append(parent_obj.product_variants.first())
        if context["related_products"] == []:
            context["related_products"] = None
        context["product_counts"] = product_variant.products.count()

        first_product = product_variant.products.first()

        context["first_product"] = first_product
        context["first_product_available_in_cart"] = cart.is_available(first_product)

        context["products"] = product_variant.products.all()[1:]
        context["item_quantity"] = cart.get_item_quantity(first_product)
        context["item_total_price_before_discount"] = (
            cart.get_item_quantity(first_product) * first_product.initial_price
        )
        context["item_total_price"] = cart.get_item_quantity(first_product) * first_product.final_price

        return context


class ShopView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        context = {}
        applied_ordering = []
        last_month = timezone.now() - timedelta(days=30)
        products_qs = (
            ProductVariant.objects.select_related("parent_product")
            .prefetch_related("products")
            .with_display_price()
            .all()
        )
        products_qs = products_qs.annotate(
            paid_items_count=Coalesce(
                Sum(
                    "products__order_items__quantity",
                    filter=Q(
                        products__order_items__order__is_paid=True,
                    ),
                ),
                Value(0),
            ),
            recent_sales=Coalesce(
                Sum(
                    "products__order_items__quantity",
                    filter=Q(
                        products__order_items__order__datetime_created__gte=last_month,
                    ),
                ),
                Value(0),
            ),
        )
        product_filter = ProductFilter(request.GET, queryset=products_qs)
        products = product_filter.qs

        if product_filter.is_valid():
            applied_ordering = product_filter.form.cleaned_data.get("ordering") or []

        if not applied_ordering:
            applied_ordering = ["popular"]

        paginator = Paginator(products, 3)
        page_number = self.request.GET.get("page")
        products_filter_by_page_number = paginator.get_page(page_number)
        context["products_by_page"] = products_filter_by_page_number
        product_counter = products.aggregate(count_all_products=Count("id"))
        context["count_all_products"] = product_counter.get("count_all_products")
        context["applied_ordering"] = applied_ordering

        return render(request, template_name="products/shop.html", context=context)


def product_selector_view(request, pk):
    cart = get_cart(request)
    product = Product.objects.filter(pk=pk).first()
    product_available_in_cart = cart.is_available(product)
    item_quantity = cart.get_item_quantity(product)
    item_total_price = item_quantity * product.final_price
    context = {
        "product": product,
        "product_available_in_cart": product_available_in_cart,
        "item_quantity": item_quantity,
        "item_total_price": item_total_price,
    }
    return render(request, template_name="products/partials/update_response_on_color.html", context=context)
