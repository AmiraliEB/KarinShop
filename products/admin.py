from django.contrib import admin
from .models import Product, ProductImage

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'discount_price', 'stock', 'is_available', 'is_amazing', 'is_best_selling', 'datetime_created', 'datetime_modified')
    list_filter = ('is_available', 'is_amazing', 'is_best_selling', 'datetime_created')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    # inlines = [ProductImageInline]

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    readonly_fields = ('image_preview',)

admin.site.register(ProductImage)