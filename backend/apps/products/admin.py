from django.contrib import admin

from . import models
from .forms import ProductImageFormSet, ProductParentAdminForm, ProductVariantAdminForm, ProductVariantFormSet


class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 0
    formset = ProductImageFormSet
    min_num = 5
    validate_min = True


class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 0
    fields = ("attribute_values",)
    filter_horizontal = ("attribute_values",)
    formset = ProductVariantFormSet


class ProductInline(admin.TabularInline):
    model = models.Product
    extra = 0
    fields = ("color", "initial_price", "discount_type", "discount_value", "stock", "product_variant")


class AttributeRuleInline(admin.TabularInline):
    model = models.AttributeRule
    extra = 1
    autocomplete_fields = ["category", "brand"]


class AttributeValueInline(admin.TabularInline):
    model = models.AttributeValue
    extra = 1


@admin.register(models.ProductParent)
class ProductParentAdmin(admin.ModelAdmin):
    form = ProductParentAdminForm

    list_display = (
        "name",
        "category",
        "brand",
    )
    filter_horizontal = ("specification_values",)
    list_filter = ("category", "brand", "datetime_created")
    search_fields = ("name", "category__name", "brand__name")
    readonly_fields = ("datetime_created", "datetime_modified")
    inlines = [ProductImageInline, ProductVariantInline]

    fieldsets = (
        (None, {"fields": ("name", "category", "brand", "specification_values")}),
        ("Advanced Options", {"fields": ("datetime_created", "datetime_modified")}),
    )
    readonly_fields = ("datetime_created", "datetime_modified")


@admin.register(models.ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    form = ProductVariantAdminForm
    list_display = ("id", "parent_product", "_full_name")
    list_display_links = ("parent_product",)
    list_filter = ("parent_product__category", "parent_product__brand")
    search_fields = ("parent_product__name", "id", "_full_name")
    readonly_fields = ("_full_name", "datetime_created", "datetime_modified", "is_available")
    autocomplete_fields = ("parent_product",)
    filter_horizontal = ("attribute_values",)
    list_select_related = ("parent_product",)
    inlines = [ProductInline]


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "product_variant", "final_price", "stock", "is_available")
    list_display_links = ("product_variant",)
    list_filter = ("is_available", "final_price")
    search_fields = ("product_variant__parent_product__name", "id", "product_variant__full_name")
    readonly_fields = ("is_available", "final_price")
    autocomplete_fields = ("product_variant",)
    list_select_related = ("product_variant", "product_variant__parent_product")


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "parent")
    search_fields = ("name", "code")


@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "attribute_category")
    search_fields = ("name",)
    inlines = [AttributeRuleInline, AttributeValueInline]


@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(models.AttributeCategory)
class AttributeCategory(admin.ModelAdmin):
    list_display = ("id", "name", "sort_order")
    ordering = ("sort_order", "id")


@admin.register(models.Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "parent_product", "rating", "is_recommend", "datetime_created", "is_approved")
    list_filter = ("is_recommend", "rating", "datetime_created")
    search_fields = ("title", "content", "parent_product__name")
    readonly_fields = ("datetime_created", "datetime_modified")


admin.site.register(models.Color)
