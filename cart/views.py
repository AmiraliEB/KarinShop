from django.shortcuts import render
from django.views.generic import View

from .forms import CartAddPrproductForm
from .cart import Cart
from django.shortcuts import get_object_or_404

class CartView(View):
    def get(self, request, *args, **kwargs):
        return render(request,'cart/cart.html')
    def post(self,request, *args, **kwargs):
        form = CartAddPrproductForm(request.POST)
        cart = Cart(request)
        pk = self.kwargs['pk']
        product = get_object_or_404()

        if form.is_valid():
            cart.add()