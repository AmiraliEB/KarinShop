from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    pass


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, verbose_name=_(""), on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(verbose_name=_("first name"), max_length=50)
    last_name = models.CharField(verbose_name=_("last name"), max_length=50)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))


class Address(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name=_("user"), on_delete=models.CASCADE, related_name="addresses")
    province = models.CharField(verbose_name=_("province"), max_length=50)
    city = models.CharField(verbose_name=_("city"), max_length=50)
    postal_code = models.CharField(max_length=20, verbose_name=_("postal code"))
    full_address = models.CharField(verbose_name=_("full address"), max_length=255)
    phone_number = models.CharField(max_length=20, verbose_name=_("phone number"), blank=True, null=True)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def get_full_address(self):
        return f"{self.province}, {self.city}, {self.full_address}"
