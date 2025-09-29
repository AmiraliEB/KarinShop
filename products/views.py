from django.shortcuts import render
from django.urls import reverse
from django.views import generic
from products.models import Product, ProductImage
from django.shortcuts import get_object_or_404, redirect
from django.utils.text import slugify

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
    template_name = "products/product-details.html"
    context_object_name = "product"
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.select_related(
            'parent_name__brand',
            'parent_name__category'
        ).prefetch_related(
            'parent_name__images',
            'attribute_values__attribute',
            'color'
        )
