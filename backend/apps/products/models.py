from __future__ import annotations

from collections import defaultdict
from math import ceil
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg, Count, Min, Q, QuerySet
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def product_image_upload_to(instance, filename):
    return f"products/{slugify(instance.parent_product.name)}/{filename}"


class ProductVariantQuerySet(models.QuerySet):
    def with_display_price(self):
        return self.annotate(min_final_price=Min("products__final_price", filter=Q(products__is_available=True)))


class ProductParent(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("parent product name"))
    category = models.ForeignKey(
        "ProductCategory",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="product_parents",
        verbose_name=_("category"),
    )
    brand: models.ForeignKey[Brand] = models.ForeignKey(
        "Brand", on_delete=models.PROTECT, related_name="product_parents", verbose_name=_("brand")
    )

    specification_values: models.ManyToManyField[AttributeValue, ProductParent] = models.ManyToManyField(
        "AttributeValue",
        related_name="parent_products",
        verbose_name=_("shared specifications"),
        blank=True,
        limit_choices_to={"attribute__show_in_specifications": True, "attribute__is_variant_defining": False},
    )

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def __str__(self):
        return self.name

    @property
    def grouped_specifications(self):
        if hasattr(self, "sorted_attribute_values"):
            values_list = self.sorted_attribute_values
        else:
            values_list = self.specification_values.select_related("attribute__attribute_category").order_by(
                "attribute__attribute_category__sort_order"
            )

        grouped_attributes = defaultdict(list)
        for value_obj in values_list:
            category = value_obj.attribute.attribute_category
            grouped_attributes[category].append(value_obj)

        return dict(grouped_attributes)

    class Meta:
        verbose_name = _("parent product")
        verbose_name_plural = _("parent products")
        ordering = ["category", "brand", "name"]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        products = self.product_variants.all()
        for product in products:
            new_full_name = product._generate_full_name()
            if product._full_name != new_full_name:
                product._full_name = new_full_name
                product.save(update_fields=["_full_name"])

    @property
    def get_main_image(self: ProductParent) -> ProductImage | None:
        images: QuerySet[ProductImage] = self.images
        if images is None:
            return None
        main_image: ProductImage | None = images.filter(is_main_image=True).first()
        return main_image.image.url if main_image is not None else None

    @property
    def get_second_image(self: ProductParent) -> ProductImage | None:
        images: QuerySet[ProductImage] = self.images
        if images is None:
            return None
        second_image: ProductImage | None = images.exclude(is_main_image=True).first()
        return second_image.image.url if second_image is not None else None

    def get_average_rate(self: ProductParent, comments_query: "QuerySet[Comments]|None" = None) -> int | str:
        if comments_query is None:
            comments: QuerySet[Comments] = self.comments
            if comments is not None:
                comments = comments.filter(is_approved=True).order_by("-datetime_created")
        else:
            comments = comments_query
        average_rating = comments.aggregate(average_rating=Avg("rating"))
        average_rating_data = average_rating.get("average_rating")
        if average_rating_data is not None:
            return "{:.2f}".format(average_rating_data)
        else:
            return 0

    def get_comment_count(self: ProductParent, comments_query: "QuerySet[Comments]|None" = None) -> Any | None:
        if comments_query is None:
            comments: QuerySet[Comments] = self.comments
            if comments is not None:
                comments = comments.filter(is_approved=True).order_by("-datetime_created")
        else:
            comments = comments_query
        comment_count = comments.aggregate(comment_count=Count("id"))
        comment_count_data = comment_count.get("comment_count")
        return comment_count_data if comment_count_data is not None else 0


class ProductVariant(models.Model):
    parent_product: models.ForeignKey[ProductParent] = models.ForeignKey(
        "ProductParent", on_delete=models.PROTECT, related_name="product_variants", verbose_name=_("product name")
    )

    _full_name = models.CharField(max_length=500, blank=True, verbose_name=_("Full Name (Cached)"))

    is_available = models.BooleanField(_("is available?"))
    is_amazing = models.BooleanField(default=False, verbose_name=_("is amazing?"))

    attribute_values: models.ManyToManyField[AttributeValue, ProductVariant] = models.ManyToManyField(
        "AttributeValue", verbose_name=_("attribute values"), limit_choices_to={"attribute__is_variant_defining": True}
    )

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    objects = ProductVariantQuerySet.as_manager()

    class Meta:
        verbose_name = _("product variant")
        verbose_name_plural = _("product variants")

    def min_price_product(self):
        available_products = [product for product in self.products.all() if product.is_available]
        if not available_products:
            return False
        return min(available_products, key=lambda p: p.final_price)

    def has_discount(self):
        product = self.min_price_product()
        if product:
            return product.has_discount()
        else:
            return False

    def discount_percentage(self):
        product = self.min_price_product()
        if product:
            return product.discount_percentage()
        else:
            return 0

    @property
    def initial_price(self):
        products = self.products.filter(is_available=True)
        if products:
            return min(product.initial_price for product in products)
        return 0

    @property
    def final_price(self):
        products = self.products.filter(is_available=True)
        if products:
            return min(product.final_price for product in products)
        return 0

    def __str__(self):
        return self._full_name if self._full_name else f"Product {self.id}"

    def get_absolute_url(self):
        return reverse("products:post_redirect", kwargs={"pk": self.pk})

    @property
    def full_name(self):
        return self._full_name

    def _generate_full_name(self):
        base_name = f"{self.parent_product.category} {self.parent_product.brand} {self.parent_product.name}"

        product_category = self.parent_product.category
        product_brand = self.parent_product.brand

        if not product_category:
            return base_name

        applicable_rules_query = Q(attributerule__category=product_category, attributerule__brand=product_brand) | Q(
            attributerule__category=product_category, attributerule__brand__isnull=True
        )

        main_feature_attributes = Attribute.objects.filter(
            applicable_rules_query, attributerule__is_main_feature=True
        ).distinct()
        main_specification_values = self.parent_product.specification_values.filter(
            attribute__in=main_feature_attributes
        ).select_related("attribute")
        main_attribute_values = self.attribute_values.filter(attribute__in=main_feature_attributes).select_related(
            "attribute"
        )
        main_values = main_attribute_values | main_specification_values
        final_parts = list()
        for attribute_value_obj in main_values:
            attribute_value = attribute_value_obj.value
            final_parts.append(attribute_value)

        return f"{base_name} {' '.join(final_parts)}".strip()

    def save(self, *args, **kwargs):
        if self.pk:
            product_counter = self.products.count()
            for product in self.products.all():
                product_counter -= 1
                if product.is_available is True:
                    self.is_available = True
                    break
                if product_counter == 0:
                    if self.is_available is True:
                        self.is_available = False
        elif self.is_available is None:
            self.is_available = False
        # product variant should be saved once before create full name (full name needs attribute values)
        super().save(*args, **kwargs)
        new_full_name = self._generate_full_name()
        if self._full_name != new_full_name:
            self._full_name = new_full_name
            super().save(update_fields=["_full_name"])


class ProductImage(models.Model):
    parent_product: models.ForeignKey[ProductParent] = models.ForeignKey(
        ProductParent, on_delete=models.CASCADE, related_name="images", verbose_name=_("parent product")
    )
    image = models.ImageField(upload_to=product_image_upload_to, verbose_name=_("product image"))
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("alt text"))
    is_main_image = models.BooleanField(default=False, verbose_name=_("is main image?"))

    def __str__(self):
        return f"Image for {self.parent_product.name}"

    def clean(self):
        if self.parent_product is None:
            raise ValidationError({"parent_product": _("Parent product must be set for the image.")})
        if not self.image:
            raise ValidationError({"image": _("Image file must be provided.")})

    class Meta:
        verbose_name = _("product image")
        verbose_name_plural = _("product images")
        constraints = [
            models.UniqueConstraint(
                fields=["parent_product"],
                condition=Q(is_main_image=True),
                name="unique_main_image_per_product",
            )
        ]


class ProductCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("category name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("category code"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="children",
        verbose_name=_("parent category"),
    )

    attribute_categories: models.ManyToManyField[AttributeCategory, ProductCategory] = models.ManyToManyField(
        "AttributeCategory", blank=True, verbose_name=_("attribute categories")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("product category")
        verbose_name_plural = _("product categories")
        ordering = ["name"]


class Product(models.Model):
    DISCOUNT_TYPE_CHOICE = (
        ("percentage", _("Percentage")),
        ("amount", _("Fixed Amount")),
    )

    product_variant: models.ForeignKey[ProductVariant] = models.ForeignKey(
        ProductVariant, verbose_name=_("Product Variant"), on_delete=models.CASCADE, related_name="products"
    )
    color = models.ForeignKey("Color", verbose_name=_("Color"), on_delete=models.CASCADE)

    initial_price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_("price (Toman)"))
    discount_type = models.CharField(
        verbose_name=_("discount type"), max_length=50, choices=DISCOUNT_TYPE_CHOICE, default="amount"
    )
    discount_value = models.PositiveIntegerField(verbose_name=_("discount value"), default=0)
    final_price = models.DecimalField(verbose_name=_("final price"), max_digits=11, decimal_places=0, null=True)

    stock = models.PositiveIntegerField(default=0, verbose_name=_("stock"))

    is_available = models.BooleanField(_("is available?"))

    def clean(self):
        if self.discount_type == "amount" and self.discount_value <= 100 and self.discount_value > 0:
            raise ValidationError({"discount_value": _("fixed amount discount values should be more than 100")})

        if self.discount_type == "percentage" and self.discount_value > 100:
            raise ValidationError({"discount_value": _("percentage discount values should be less than 100")})

    def discount_percentage(self):
        discount_percentage = 0
        if self.discount_type == "percentage":
            return self.discount_value
        elif self.discount_type == "amount":
            if self.discount_value and self.final_price > 0 and self.discount_value < self.initial_price:
                percentage = (self.discount_value / self.initial_price) * 100
                discount_percentage = ceil(percentage)
            return discount_percentage

    def has_discount(self):
        if self.discount_value > 0 and self.discount_value < self.initial_price:
            return True
        return False

    def save(self, *args, **kwargs):
        if not self.has_discount():
            self.final_price = self.initial_price
        else:
            if self.discount_type == "percentage":
                final_price = self.initial_price - ((self.initial_price * self.discount_value) / 100)
                self.final_price = final_price
            elif self.discount_type == "amount":
                final_price = self.initial_price - self.discount_value
                self.final_price = final_price

        self.is_available = self.stock > 0
        super().save(*args, **kwargs)
        if self.is_available is not self.product_variant.is_available:
            product_counter = self.product_variant.products.count()
            for product in self.product_variant.products.all():
                product_counter -= 1
                if product.is_available is True:
                    self.product_variant.is_available = True
                    self.product_variant.save()
                    break
                if product_counter == 0:
                    if self.product_variant.is_available is True:
                        self.product_variant.is_available = False
                        self.product_variant.save()

    def get_absolute_url(self):
        return reverse("products:post_redirect", kwargs={"pk": self.product_variant.pk})

    def __str__(self):
        return f"{self.product_variant.full_name} {self.color}"


class Attribute(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("attribute name"))
    # important: this field is for prevent hardcode name in queries , value should change with cautious
    code = models.CharField(max_length=20, verbose_name=_("code for lookup (DO NOT CHANGE THE VALUE!)"))
    product_category: models.ManyToManyField[ProductCategory, Attribute] = models.ManyToManyField(
        ProductCategory, related_name="attributes", verbose_name=_("related categories"), through="AttributeRule"
    )

    attribute_category = models.ForeignKey(
        "AttributeCategory",
        related_name="attributes",
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name=_("attribute category"),
    )
    is_variant_defining = models.BooleanField(default=False, verbose_name=_("Is this a variant-defining attribute?"))
    show_in_specifications = models.BooleanField(_("Show in specifications in detail page?"), default=True)

    # this allows multiple values for an attribute in a product (e.g. color: red, blue)
    allow_multiple_values = models.BooleanField(
        default=False, verbose_name=_("امکان انتخاب چند مقدار همزمان در واریانت")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attribute")
        verbose_name_plural = _("attributes")
        ordering = ["attribute_category"]


class AttributeRule(models.Model):
    attribute: models.ForeignKey[Attribute] = models.ForeignKey(
        "Attribute", verbose_name=_("attribute"), on_delete=models.CASCADE
    )
    category: models.ForeignKey[ProductCategory] = models.ForeignKey(
        "ProductCategory", verbose_name=_("category"), on_delete=models.CASCADE
    )
    brand = models.ForeignKey("Brand", verbose_name=_("brand"), on_delete=models.CASCADE, blank=True, null=True)

    is_main_feature = models.BooleanField(default=False, verbose_name=_("Show in product tite?"))

    class Meta:
        verbose_name = _("Attribute Rule")
        verbose_name_plural = _("Attribute Rules")
        constraints = [
            models.UniqueConstraint(fields=["attribute", "category", "brand"], name="unique_attribute_category_brand"),
            models.UniqueConstraint(
                fields=["attribute", "category"],
                condition=Q(brand__isnull=True),
                name="unique_attribute_category_when_brand_is_null",
            ),
        ]

    def __str__(self):
        if self.brand:
            return f"{self.attribute.name} for {self.category.name} {self.brand.name}"
        return f"{self.attribute.name} for {self.category.name}"


class AttributeValue(models.Model):
    attribute: models.ForeignKey[Attribute] = models.ForeignKey(
        Attribute, on_delete=models.CASCADE, related_name="values", verbose_name=_("attribute")
    )
    value = models.CharField(max_length=255, verbose_name=_("attribute value"))

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        verbose_name = _("attribute value")
        verbose_name_plural = _("attribute values")
        unique_together = ("value", "attribute")
        ordering = ["attribute__id"]


class AttributeCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("category name"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("sort order"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("attribute category")
        verbose_name_plural = _("attribute categories")
        ordering = ["id"]


class Brand(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("brand"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("brand code"))
    category = models.ManyToManyField(ProductCategory, related_name="brands", verbose_name=_("related categories"))

    def __str__(self):
        return self.name


class Comments(models.Model):
    parent_product: models.ForeignKey[ProductParent] = models.ForeignKey(
        ProductParent, on_delete=models.CASCADE, related_name="comments", verbose_name=_("product")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments", verbose_name=_("user"))

    title = models.CharField(_("title"), max_length=200)
    content = models.TextField(verbose_name=_("comment content"))
    rating = models.PositiveSmallIntegerField(
        verbose_name=_("rating"), validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    is_recommend = models.BooleanField(default=None, verbose_name=_(""), null=True, blank=True)
    is_approved = models.BooleanField(default=False, verbose_name=_("is approved by admin?"))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ["-datetime_created"]

    def __str__(self):
        return f"Comment by {self.user} on {self.parent_product}"


class Color(models.Model):
    color_name = models.CharField(_("Color Name"), max_length=50)
    hex_code = models.CharField(_("Hex Code"), max_length=50, unique=True, null=False)

    def __str__(self):
        return f"{self.color_name}"


@receiver(m2m_changed, sender=ProductVariant.attribute_values.through)
def update_full_name_on_m2m_change(sender, instance, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        new_full_name = instance._generate_full_name()
        if instance._full_name != new_full_name:
            instance._full_name = new_full_name
            instance.save(update_fields=["_full_name"])


@receiver([post_save, post_delete], sender=AttributeRule)
def update_product_names_on_rule_change(sender, instance, **kwargs):
    category = instance.category
    brand = instance.brand
    if brand:
        affected_parent_products = ProductParent.objects.filter(category=category, brand=brand)
    else:
        affected_parent_products = ProductParent.objects.filter(category=category)
    affected_products = ProductVariant.objects.filter(parent_product__in=affected_parent_products).iterator()
    for product in affected_products:
        new_full_name = product._generate_full_name()
        if product._full_name != new_full_name:
            product._full_name = new_full_name
            product.save(update_fields=["_full_name"])
