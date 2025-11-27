from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from . import models
from .forms import ProductAdminForm, ProductImageFormSet, ProductFormSet, ParentProductAdminForm

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 0
    formset = ProductImageFormSet
    min_num = 5
    validate_min = True

class ProductInline(admin.TabularInline):
    model = models.Product
    extra = 0
    fields = ('price', 'stock', 'is_available', 'attribute_values')
    readonly_fields = ('is_available',)
    filter_horizontal = ('attribute_values',)
    formset = ProductFormSet

class AttributeRuleInline(admin.TabularInline):
    model = models.AttributeRule
    extra = 1
    autocomplete_fields = ['category', 'brand']

class AttributeValueInline(admin.TabularInline):
    model = models.AttributeValue
    extra = 1 

@admin.register(models.ParentProduct)
class ParentProductAdmin(admin.ModelAdmin):
    form = ParentProductAdminForm

    list_display = ('name', 'category', 'brand',)
    filter_horizontal = ('specification_values',)
    list_filter = ('category', 'brand', 'datetime_created')
    search_fields = ('name', 'category__name', 'brand__name')
    readonly_fields = ('datetime_created','datetime_modified')
    inlines = [ProductImageInline,ProductInline]

    fieldsets = (
        (None, {'fields': ('name', 'category', 'brand','specification_values')}),
        ('Advanced Options', {'fields': ('datetime_created', 'datetime_modified')}),
    )
    readonly_fields = ('datetime_created', 'datetime_modified')


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display =('id','parent_product', '_full_name', 'final_price', 'stock', 'is_available')
    list_display_links = ('parent_product',)
    list_filter = ('is_available','final_price', 'parent_product__category', 'parent_product__brand')
    search_fields = ('parent_product__name', 'id','_full_name')
    readonly_fields = ('_full_name' ,'datetime_created', 'datetime_modified', 'is_available', 'final_price')
    autocomplete_fields = ('parent_product',)
    filter_horizontal = ('attribute_values',)
    list_select_related = ('parent_product',)


@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'parent')
    search_fields = ('name', 'code')

@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name','attribute_category')
    search_fields = ('name',)
    inlines = [AttributeRuleInline,AttributeValueInline]

@admin.register(models.Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(models.AttributeCategory)
class AttributeCategory(admin.ModelAdmin):
    list_display = ('id','name','sort_order')
    ordering = ('sort_order','id')

@admin.register(models.Comments)
class CommentsAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'parent_product', 'rating', 'is_recommend', 'datetime_created','is_approved')
    list_filter = ('is_recommend', 'rating', 'datetime_created')
    search_fields = ('title', 'content', 'parent_product__name')
    readonly_fields = ('datetime_created', 'datetime_modified')