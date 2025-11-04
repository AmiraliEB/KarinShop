from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    pass
class Profile(models.Model):
    user = models.OneToOneField(CustomUser, verbose_name=_(""), on_delete=models.CASCADE,related_name='profile')
    first_name = models.CharField(verbose_name=_("first name"), max_length=50)
    last_name = models.CharField(verbose_name=_("last name"), max_length=50)

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

class Address(models.Model):
    user = models.ForeignKey(CustomUser, verbose_name=_("addresses"), on_delete=models.CASCADE,related_name='addresses')
    province = models.CharField(verbose_name=_("province"), max_length=50)
    city = models.CharField(verbose_name=_("city"), max_length=50)
    postal_code = models.PositiveIntegerField(verbose_name=_("postal code"))
    full_address = models.CharField(verbose_name=_("full address"), max_length=255)
    phone_number = models.PositiveIntegerField(_(""))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))
