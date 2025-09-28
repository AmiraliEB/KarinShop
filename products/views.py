from django.shortcuts import render
from django.views import generic
from products.models import Product, ProductCategory
from django.shortcuts import get_object_or_404, redirect

def post_redirect_view(request, pk):
    product_obj = get_object_or_404(Product, pk=pk)
    return redirect(product_obj.get_absolute_url(), permanent=True)

class ProductDetailView(generic.DetailView):
    model = Product
    template_name = "products/product-details.html"
    context_object_name = "product"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get('pk')
        product_obj = get_object_or_404(Product, pk=pk)

        context['category'] = product_obj.category
        return context

