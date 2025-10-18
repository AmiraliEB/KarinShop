from django.urls import reverse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _
from allauth.account.views import PasswordResetView, PasswordResetDoneView,EmailVerificationSentView,AccountInactiveView,PasswordResetFromKeyDoneView
from django.contrib import messages
from django.views import View
from allauth.account.models import EmailAddress
from allauth.account.adapter import get_adapter
from django.contrib.auth import get_user_model
from allauth.utils import build_absolute_uri

User = get_user_model()

from accounts.forms import ResendConfirmationEmailForm
#TODO: bug:user can get message with get method on any custom views
    
def custom_resend_email(request, email, template_prefix, context):
    try:
        adapter = get_adapter(request)
        adapter.send_mail(template_prefix,email,context)
    except Exception as e:
        print(f"error in send custom email allauth: {e}")
    

class CustomPasswordResetView(PasswordResetView):
    def form_valid(self, form):
        response = super().form_valid(form)
        return redirect(reverse('account_login'))

class CustomAccountInactiveView(AccountInactiveView):
    def get(self, request, *args, **kwargs):
        messages.error(request, _("اکانت شما غیرفعال شده است. لطفا با پشتیبانی تماس بگیرید."))
        return redirect(reverse('account_login'))

class CustomPasswordResetFromKeyDoneView(PasswordResetFromKeyDoneView):
    def get(self, request, *args, **kwargs):
        return redirect(reverse('account_login'))
    
class ResendConfirmationEmailView(View):
    template_name = "account/resend_confirmation_email.html"

    def get(self, request, *args, **kwargs):
        form = ResendConfirmationEmailForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = ResendConfirmationEmailForm(request.POST)
    
        if form.is_valid():
            email = form.cleaned_data['email'] 
            
            try:
                email_address = EmailAddress.objects.get(email__iexact=email)
                if email_address.verified:
                    custom_resend_email(request,email,'account/email/account_already_exists',{'password_reset_url': build_absolute_uri(request, reverse('account_reset_password'))})
                else:
                    email_address.send_confirmation(request)
            except EmailAddress.DoesNotExist:
                    custom_resend_email(request,email,'account/email/unknown_account',{'signup_url': build_absolute_uri(request, reverse('account_signup'))})
            return redirect('account_resend_confirmation_done')
        return render(request, self.template_name, {'form': form})
    
class ResendConfirmationEmailDoneView(View):
    template_name = "account/account_resend_confirmation_done.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)
    