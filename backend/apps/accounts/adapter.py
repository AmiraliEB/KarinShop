from types import SimpleNamespace

from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings


class CustomAccountAdapter(DefaultAccountAdapter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_messages["inactive_account"] = "حساب کاربری شما غیرفعال است و امکان بازیابی رمز عبور وجود ندارد."

    def add_message(self, request, level, message_template, message_context=None, extra_tags=""):
        if message_template == "account/messages/email_confirmation_sent.txt":
            return
        super().add_message(request, level, message_template, message_context, extra_tags)

    def render_mail(self, template_prefix, email, context, headers=None):
        context["current_site"] = SimpleNamespace(
            domain=settings.SITE_DOMAIN,
            name=settings.SITE_NAME,
        )
        return super().render_mail(template_prefix, email, context, headers=headers)
