from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Address, CustomUser, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Profile"


class AddressInline(admin.TabularInline):
    model = Address
    extra = 1


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = (
        "email",
        "is_staff",
        "is_active",
    )
    list_filter = (
        "email",
        "is_staff",
        "is_active",
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "is_staff", "is_active", "groups", "user_permissions"),
            },
        ),
    )
    search_fields = ("email",)
    ordering = ("email",)

    inlines = [ProfileInline, AddressInline]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Address)
