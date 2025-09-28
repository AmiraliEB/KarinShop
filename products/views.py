from django.shortcuts import render
from django.views import generic
from products.models import Product
from django.shortcuts import get_object_or_404, redirect

def post_redirect_view(request, pk):
    print(Product.objects.all())
    product_obj = get_object_or_404(Product, pk=pk)
    return redirect(product_obj.get_absolute_url(), permanent=True)

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product-details.html"
    context_object_name = "product"

