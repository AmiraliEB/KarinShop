from django.contrib import admin
from . import models

@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'stock', 'is_available', 'is_amazing', 'is_best_selling', 'datetime_created', 'datetime_modified')
    list_filter = ('is_available', 'is_amazing', 'is_best_selling', 'datetime_created')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    # inlines = [ProductImageInline]

class ProductImageInline(admin.TabularInline):
    model = models.ProductImage
    extra = 1
    readonly_fields = ('image_preview',)

admin.site.register(models.ProductImage)

@admin.register(models.ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    search_fields = ('name',)
    readonly_fields = ('slug',)
    # prepopulated_fields = {'slug': ('name',)}