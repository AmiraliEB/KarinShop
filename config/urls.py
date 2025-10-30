"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, reverse_lazy
from django.conf import settings
from django.conf.urls.static import static
from allauth.account.views import PasswordResetView

from accounts.views import CustomAccountInactiveView, CustomPasswordResetFromKeyDoneView, ResendConfirmationEmailView, ResendConfirmationEmailDoneView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/password/reset', PasswordResetView.as_view(success_url=reverse_lazy('account_login')), name='account_reset_password'),
    path("accounts/inactive/", CustomAccountInactiveView.as_view(), name="account_inactive"),
    path("accounts/password/reset/key/done/",CustomPasswordResetFromKeyDoneView.as_view(),name="account_reset_password_from_key_done"),
    path('accounts/resend-confirmation/', ResendConfirmationEmailView.as_view(), name='account_resend_confirmation'),
    path('accounts/resend-confirmation/done/', ResendConfirmationEmailDoneView.as_view() , name='account_resend_confirmation_done'),
    path('accounts/', include('allauth.urls')),
    path('', include('core.urls')),
    path('', include('products.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
