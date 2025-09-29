from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from . import models

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1

@admin.register(models.ParentProduct)
class ParentProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','brand','slug')
    readonly_fields = ('slug','datetime_created','datetime_modified')
    inlines = [ProductImageInline]

    fieldsets = (
        (None, {
            'fields':('name','category','brand',)
        }),
        (None, {
            'fields':('slug',)
        }),
        (None, {
            'fields':('datetime_created','datetime_modified',)
        })
    )


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','parent_product','slug')
    search_fields = ('name', 'description')
    readonly_fields = ('slug','datetime_created', 'datetime_modified')

    filter_horizontal = ('color', 'attribute_values',)
    fieldsets = (
        (None, {
            'fields': ('parent_product',)
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
    list_display = ('name','code', 'parent')
    search_fields = ('name',)
    readonly_fields = ('slug',)

@admin.register(models.AttributeValue)
class AttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value')
    search_fields = ('value', 'attribute__name')
    ordering = ('attribute__name', 'value')

class AttributeValueInline(admin.TabularInline):
    model = models.AttributeValue
    extra = 1
    
@admin.register(models.Attribute)
class AttributeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    inlines = [AttributeValueInline]

@admin.register(models.Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(models.Brand)