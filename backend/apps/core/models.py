from django.db import models
from django.utils.translation import gettext_lazy as _


class HomePageModel(models.Model):
    # TODO: limit height and width for banner
    banner = models.ImageField(_("Banner"), upload_to="core/banner", max_length=None)
