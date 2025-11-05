from django import forms
from django.utils.translation import gettext_lazy as _
from accounts.models import Address
from django.core.validators import RegexValidator
class CartAddPrproductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        initial=1,
        widget=forms.NumberInput(
            attrs={
                'class': 'custom-input text-lg bg-transparent border-none focus:ring-0 text-center w-full cursor-default ',
                'id': 'customInput',
                'readonly': True,
                'style': 'pointer-events: none;',
            }
        )
    )

class CartAddAddressFrom(forms.Form):
    phone_number_validator = RegexValidator(
        regex= r'^09[0-9]{9}$',
        message= "شماره موبایل باید ۱۱ رقمی باشد و با 09 شروع شود.",
    )
    postal_code_validator = RegexValidator(
    regex=r'^[0-9]{10}$',
    message="کد پستی باید ۱۰ رقمی و فقط شامل اعداد باشد."
    )

    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)

    province = forms.CharField(max_length=50, required=True)
    city = forms.CharField(max_length=50, required=True)
    postal_code = forms.IntegerField(required=False, validators=[postal_code_validator])
    full_address = forms.CharField(max_length=255)
    phone_number = forms.IntegerField(required=True,validators=[phone_number_validator])

