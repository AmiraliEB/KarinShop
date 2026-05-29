import django_filters
from products.models import ProductVariant


class ProductFilter(django_filters.FilterSet):
    amazing = django_filters.BooleanFilter(field_name="is_amazing", lookup_expr="exact")
    ordering = django_filters.OrderingFilter(fields=(("best_seller", "paid_items_count"),))

    class Meta:
        model = ProductVariant
        fields = ["is_amazing"]

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
