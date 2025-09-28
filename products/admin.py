from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from . import models

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('category',)
    search_fields = ('name', 'description')
    readonly_fields = ('slug','datetime_created', 'datetime_modified')
    inlines = [ProductImageInline]

    fieldsets = (
        (None, {
            'fields': ('name', 'category',)
        }),
        (None, {
            'fields': ('price','discount_price', 'stock')
        }),
        (None, {
            'fields': ('is_available', 'is_amazing', 'is_best_selling')
        }),
        (None, {
            'fields': ('color', 'attribute_values')
        }),
        (None, {
            'fields': ('datetime_created', 'datetime_modified')
        }),
    )
@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    readonly_fields = ('slug',)

@admin.register(models.AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')
    search_fields = ('value', 'attribute__name')
    ordering = ('attribute__name', 'value')

@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)