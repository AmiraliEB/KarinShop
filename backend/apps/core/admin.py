from django.contrib import admin

from .models import HomePageModel


@admin.register(HomePageModel)
class HomePageModelAdmin(admin.ModelAdmin):
    list_display = ("banner",)
