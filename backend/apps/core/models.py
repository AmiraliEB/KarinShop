from django.db import models
from django.utils.translation import gettext_lazy as _


class HomePageModel(models.Model):
    banner = models.ImageField(
        _("Banner"), upload_to="core/banner", height_field="2880", width_field="600", max_length=None
    )
