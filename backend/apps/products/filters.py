import django_filters
from products.models import ProductVariant


class ProductFilter(django_filters.FilterSet):
    amazing = django_filters.BooleanFilter(field_name="is_amazing", lookup_expr="exact")
    available = django_filters.BooleanFilter(field_name="is_available", lookup_expr="exact")
    ordering = django_filters.OrderingFilter(
        fields=(
            ("paid_items_count", "best_seller"),
            ("recent_sales", "popular"),
            (
                "min_final_price",
                "price",
            ),  # min_final_price is a field in ProductVariant model that returns the minimum price of the variant's products
        ),
    )
    category = django_filters.CharFilter(field_name="parent_product__category__code", lookup_expr="exact")
    has_discount = django_filters.BooleanFilter(method="filter_has_discount")

    def filter_has_discount(self, queryset, name, value):
        if value:
            return queryset.filter(products__discount_value__gt=0).distinct()
        return queryset

    class Meta:
        model = ProductVariant
        fields = ["is_amazing", "is_available"]

    # def filter_queryset(self, queryset):
    #     data = self.request.GET.copy()
    #     first_key = None
    #     for key in data.keys:
    #         if data[key]:
    #             first_key = key
    #             break
    #     if first_key:
    #         for key in list(data.keys()):
    #             if key != first_key:
    #                 del data[key]
    #     self._form = self.get_form_class()(data=data)
    #     self._form.is_valid()
    #     return super().filter_queryset(queryset)
