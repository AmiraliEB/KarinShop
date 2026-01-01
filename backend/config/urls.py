from accounts.views import (
    CustomAccountInactiveView,
    CustomPasswordResetFromKeyDoneView,
    ResendConfirmationEmailDoneView,
    ResendConfirmationEmailView,
)
from allauth.account.views import PasswordResetView
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, reverse_lazy

urlpatterns = [
    path("admin/", admin.site.urls),
    path(
        "accounts/password/reset",
        PasswordResetView.as_view(success_url=reverse_lazy("account_login")),
        name="account_reset_password",
    ),
    path("accounts/inactive/", CustomAccountInactiveView.as_view(), name="account_inactive"),
    path(
        "accounts/password/reset/key/done/",
        CustomPasswordResetFromKeyDoneView.as_view(),
        name="account_reset_password_from_key_done",
    ),
    path("accounts/resend-confirmation/", ResendConfirmationEmailView.as_view(), name="account_resend_confirmation"),
    path(
        "accounts/resend-confirmation/done/",
        ResendConfirmationEmailDoneView.as_view(),
        name="account_resend_confirmation_done",
    ),
    path("accounts/", include("allauth.urls")),
    path("", include("core.urls")),
    path("", include("products.urls")),
    path("cart/", include("cart.urls")),
    path("payments/", include("payments.urls")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
