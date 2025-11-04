from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView

from .forms import CartAddPrproductForm
from .cart import Cart
from products.models import Product
from django.shortcuts import get_object_or_404

class CartView(TemplateView):
    template_name = 'cart/cart.html'

class RemoveCartItemView(View):
    def get(self,request,*args, **kwargs):
        cart = Cart(request)
        pk = self.kwargs.get('pk')
        if pk is None:
           return redirect('cart_detail')
        product = Product.objects.get(pk=pk)
        cart.remove(product)
        return redirect('cart_detail')

    def post(self,request,*args, **kwargs):
        # post method is for clear all the items
        cart = Cart(request)
        cart.clear()
        return redirect('cart_detail')

class CheckoutView(TemplateView):
    template_name = "cart/checkout.html"