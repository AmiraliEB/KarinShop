from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView

from django.utils import timezone
from datetime import timedelta
from .forms import CartAddAddressFrom
from .cart import Cart
from products.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from accounts.models import Profile, Address

class CartView(TemplateView):
    template_name = 'cart/cart.html'

class RemoveCartItemView(View):
    def get(self,request,*args, **kwargs):
        cart = Cart(request)
        pk = self.kwargs.get('pk')
        if pk is None:
           return redirect('cart_detail')
        product = get_object_or_404(Product,pk=pk)
        cart.remove(product)
        return redirect('cart_detail')

    def post(self,request,*args, **kwargs):
        # post method is for clear all the items
        cart = Cart(request)
        cart.clear()
        return redirect('cart_detail')

class CheckoutView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = CartAddAddressFrom()

        today = timezone.localdate()
        time_to_leave_warehouse = today + timedelta(days=2)
        return render(request,"cart/checkout.html",{'form':form,'time_to_leave_warehouse':time_to_leave_warehouse})
    def post(self,request,*args, **kwargs):
        form = CartAddAddressFrom(request.POST)
        current_user = request.user
        profile, created = Profile.objects.get_or_create(user=current_user)

        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']

            province = form.cleaned_data['province']
            city = form.cleaned_data['city']
            postal_code = form.cleaned_data['postal_code']
            full_address = form.cleaned_data['full_address']
            phone_number = form.cleaned_data['phone_number']

            profile.user = request.user
            profile.first_name = first_name
            profile.last_name = last_name
            profile.save()

            new_address = Address()
            new_address.user = request.user
            new_address.province = province
            new_address.city = city
            new_address.postal_code = postal_code
            new_address.full_address = full_address
            new_address.phone_number = phone_number
            new_address.save()

            return redirect('payment')
        else:
            return render(request, "cart/checkout.html",{'form':form})

class PaymentView(LoginRequiredMixin, View):
    def get(self,request,*args, **kwargs):
        return render(request,template_name="cart/payment.html")