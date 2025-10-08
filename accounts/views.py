from django.urls import reverse
from django.views import View
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from allauth.account.views import SignupView, PasswordResetView, PasswordResetDoneView

class CustomSignupView(SignupView):
    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(reverse('account_login'))
    
class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _("Password reset email has been sent. Please check your inbox."))
        return redirect(reverse('account_login'))

class CustomPasswordResetDoneView(PasswordResetDoneView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('account_login'))