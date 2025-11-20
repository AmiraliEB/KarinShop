from django.shortcuts import render,redirect
from django.views.generic import View,TemplateView

from django.utils import timezone
from datetime import timedelta
from .forms import CartAddAddressFrom, CouponApplyForm
from .cart import Cart
from products.models import Product
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from accounts.models import Profile, Address
from orders.models import Coupon
from django.contrib import messages

from django.utils.translation import gettext_lazy as _
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

today = timezone.localdate()
time_to_leave_warehouse = today + timedelta(days=2)

class CheckoutView(LoginRequiredMixin,View):
    def get(self,request,*args, **kwargs):
        form = CartAddAddressFrom()
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
            return render(request, "cart/checkout.html",{'form':form, 'time_to_leave_warehouse':time_to_leave_warehouse})

class PaymentView(LoginRequiredMixin, View):
    def get(self,request,*args, **kwargs):
        coupon_form = CouponApplyForm()
        return render(request,template_name="cart/payment.html",context={'coupon_form':coupon_form, 'time_to_leave_warehouse':time_to_leave_warehouse})
    
    def post(self,request,*args, **kwargs):
        coupon_form = CouponApplyForm()
        if 'coupon_submit' in request.POST:
            coupon_form = CouponApplyForm(request.POST)
            if coupon_form.is_valid():
                coupon_code = coupon_form.cleaned_data['code']
                try:
                    coupon = Coupon.objects.get(code__iexact=coupon_code)
                    request.session['coupon_id'] = coupon.id
                    if coupon.is_usable:
                        messages.success(request, _('کد تخفیف با موفقیت اعمال شد.'))
                    else:
                        coupon_form.add_error('code', _('این کد تخفیف معتبر نیست یا قابل استفاده نمی‌باشد.'))
                except Coupon.DoesNotExist:
                    coupon_form.add_error('code', _('کد تخفیف وارد شده وجود ندارد.'))
            return render(request, "cart/payment.html",{'coupon_form':coupon_form, 'time_to_leave_warehouse':time_to_leave_warehouse,'coupon':coupon})
        return render(request,template_name="cart/payment.html",context={'coupon_form':coupon_form, 'time_to_leave_warehouse':time_to_leave_warehouse})
