from django.urls import reverse
from django.shortcuts import redirect
from django.utils.translation import gettext_lazy as _
from allauth.account.views import PasswordResetView, PasswordResetDoneView,EmailVerificationSentView,AccountInactiveView,PasswordResetFromKeyDoneView
from django.contrib import messages
#TODO: bug:user can get message with get method on any custom views
class CustomEmailVerificationSentView(EmailVerificationSentView):
    def get(self, form):
        messages.success(self.request, _("یک ایمیل برای شما فرستاده شده است. لطفا برای فعال سازی اکانت, صندوق ورودی ایمیل خود را بررسی کنید."))
        return redirect(reverse('account_login'))
    
class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(reverse('account_login'))

class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request, *args, **kwargs):
        messages.success(self.request, _("لینک بازنشانی رمز عبور برای شما ارسال شد. لطفاً صندوق ورودی و پوشه هرزنامه خود را بررسی نمایید."))
        return redirect(reverse('account_login'))

class CustomAccountInactiveView(AccountInactiveView):
    def get(self, request, *args, **kwargs):
        messages.error(request, _("اکانت شما غیرفعال شده است. لطفا با پشتیبانی تماس بگیرید."))
        return redirect(reverse('account_login'))

class CustomPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('account_login'))