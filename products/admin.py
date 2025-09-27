from django.contrib import admin
from . import models

class ProductVariantInline(admin.TabularInline):
    model = models.ProductVariant
    extra = 1 
    autocomplete_fields = ['variant_attributes'] 
class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_variable')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    inlines = [ProductVariantInline,ProductImageInline]
    readonly_fields = ('slug',)

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