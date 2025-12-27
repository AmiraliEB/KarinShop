from cart.cart import get_cart
from cart.forms import CartAddProductForm
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Prefetch
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.views import generic
from products.models import AttributeValue, Comments, ParentProduct, Product

from .forms import CommentForm


def post_redirect_view(request, pk):
    product_obj = get_object_or_404(Product, pk=pk)
    return redirect(
        "products:product_detail",
        pk=product_obj.pk,
        slug=slugify(product_obj.full_name, allow_unicode=True),
        permanent=True,
    )


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product_details.html"
    context_object_name = "product"

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object: Product = self.get_object()
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
        return queryset.select_related("parent_product__brand", "parent_product__category").prefetch_related(
            Prefetch(
                "parent_product__specification_values",
                queryset=AttributeValue.objects.select_related("attribute__attribute_category").order_by(
                    "attribute__attribute_category__sort_order"
                ),
                to_attr="sorted_attribute_values",
            ),
            "parent_product__images",
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        product = self.object

        context["discount_percentage"] = product.discount_percentage
        context["grouped_attributes"] = product.parent_product.grouped_specifications

        comments = (
            Comments.objects.filter(parent_product=product.parent_product, is_approved=True)
            .select_related("user")
            .order_by("-datetime_created")
        )
        comment_summary_data = comments.aggregate(
            average_rating=Avg("rating"),
            comment_count=Count("id"),
        )
        paginator = Paginator(comments, 5)
        page_number = self.request.GET.get("page")
        commnts_filter_by_page_number = paginator.get_page(page_number)

        context["comments"] = commnts_filter_by_page_number
        context["comments_count"] = comment_summary_data.get("comment_count")

        if comment_summary_data.get("average_rating") is not None:
            context["average_rating"] = "{:.2f}".format(comment_summary_data.get("average_rating"))
        else:
            context["average_rating"] = 0
        context["cart"] = cart

        if "comment_form" not in context:
            context["comment_form"] = CommentForm()
        if "cart_form" not in context:
            context["cart_form"] = CartAddProductForm()

        main_img_obj = product.parent_product.images.filter(is_main_image=True).first()
        context["main_image"] = main_img_obj.image.url if main_img_obj else None

        context["album_images"] = product.parent_product.images.filter(is_main_image=False)

        category = product.parent_product.category
        brand = product.parent_product.brand
        related_parent = (
            ParentProduct.objects.prefetch_related("products")
            .filter(category=category, brand=brand)
            .exclude(id=product.parent_product.id)[:6]
        )
        if not related_parent.exists():
            related_parent = (
                ParentProduct.objects.prefetch_related("products")
                .filter(category=category)
                .exclude(id=product.parent_product.id)[:6]
            )
        context["related_products"] = []
        for parent_obj in related_parent:
            context["related_products"].append(parent_obj.products.first())

        context["product_available_in_cart"] = cart.is_available(product)
        context["item_quantity"] = cart.get_item_quantity(product)
        context["item_total_price_before_discount"] = cart.get_item_quantity(product) * product.initial_price
        context["item_total_price"] = cart.get_item_quantity(product) * product.final_price

        return context


class ShopView(generic.TemplateView):
    template_name = "products/shop.html"
