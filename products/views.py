from collections import defaultdict
from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from products.models import AttributeValue, Product, AttributeCategory
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify
from django.db.models import Prefetch

def post_redirect_view(request, pk):
    product_obj = get_object_or_404(Product, pk=pk)
    return redirect(
        'products:product_detail',
        pk=product_obj.pk,
        slug=slugify(product_obj.full_name, allow_unicode=True),
        permanent=True
    )

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product_details.html"
    context_object_name = "product"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'parent_product__brand',
            'parent_product__category'
        ).prefetch_related(
                Prefetch(
                'attribute_values',
                queryset=AttributeValue.objects.select_related(
                    'attribute__attribute_category'  
                ).order_by(
                    'attribute__attribute_category__id'  
                ),
                to_attr='sorted_attribute_values' 
            ),
            'parent_product__images',
            'color',
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        discount_percentage = 0
        
        if product.discount_price and product.price > 0 and product.price > product.discount_price:
            discount_amount = product.price - product.discount_price
            percentage = (discount_amount / product.price) * 100
            discount_percentage = round(percentage) 
        context['discount_percentage'] = discount_percentage

        grouped_attributes = defaultdict(list)

        for value_obj in self.object.sorted_attribute_values:
            category = value_obj.attribute.attribute_category
            grouped_attributes[category].append(value_obj)
        context['grouped_attributes'] = dict(grouped_attributes)
        return context