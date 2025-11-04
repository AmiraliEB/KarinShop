from django import forms
from django.utils.translation import gettext_lazy as _
from accounts.models import Address
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
    first_name = forms.CharField(max_length=50, required=False)
    last_name = forms.CharField(max_length=50, required=False)
    
    province = forms.CharField(max_length=50, required=True)
    city = forms.CharField(max_length=50, required=True)
    postal_code = forms.IntegerField(required=False)
    full_address = forms.CharField(verbose_name=_("full address"), max_length=255)
    phone_number = forms.IntegerField(required=False)

