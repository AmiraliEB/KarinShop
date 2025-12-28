from django.contrib import admin

from .models import Coupon, Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    fields = ["product", "quantity", "price"]
    extra = 0
    raw_id_fields = ["product"]

    @admin.display(description="قیمت کل ردیف")
    def get_cost(self, obj):
        return f"{obj.get_cost():,} تومان"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number",
        "user",
        "phone_number",
        "is_paid",
        "status",
        "get_total_price_display",
        "datetime_created",
    ]

    list_filter = ["is_paid", "status", "datetime_created"]
    search_fields = ["order_number", "user__username", "user__email", "phone_number", "full_address"]

    inlines = [OrderItemInline]

    readonly_fields = ["datetime_created", "order_number", "get_total_price_display"]

    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("user", "order_number", "status", "is_paid")}),
        ("اطلاعات ارسال", {"fields": ("address", "province", "city", "full_address", "postal_code", "phone_number")}),
        ("تاریخچه", {"fields": ("datetime_created", "get_total_price_display")}),
    )

    @admin.display(description="مبلغ کل سفارش")
    def get_total_price_display(self, obj):
        return f"{obj.get_total_price():,} تومان"


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_value", "quantity", "used_count", "valid_from", "valid_to", "active"]
    list_filter = ["active", "valid_from", "valid_to"]
    search_fields = ["code"]
