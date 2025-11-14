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
    
    SHIPPING_CHOICES = [
        ('post', 'پست پیشتاز: 89,000 تومان'),
        ('tipax', 'تیپاکس: 120,000 تومان'),
    ]


    phone_number_validator = RegexValidator(
        regex= r'^09[0-9]{9}$',
        message= "شماره موبایل باید ۱۱ رقمی باشد و با 09 شروع شود.",
    )
    postal_code_validator = RegexValidator(
    regex=r'^[0-9]{10}$',
    message="کد پستی باید ۱۰ رقمی و فقط شامل اعداد باشد."
    )

    tailwind_classes = "block w-full py-1.5 px-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400 h-11"

    first_name = forms.CharField(max_length=50, required=True,label=_("First name"),widget=forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'نام*'}))
    last_name = forms.CharField(max_length=50, required=True, label=_("Last name"),widget=forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'نام خانوادگی*'}))

    province = forms.CharField(max_length=50, required=True, label=_("Province"),widget=forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'استان*'}))
    city = forms.CharField(max_length=50, required=True, label=_("City"),widget=forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'شهر*'}))
    postal_code = forms.CharField(max_length=20,required=True, validators=[postal_code_validator], label=_("Postal code"),widget=forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'کد پستی*'}))
    full_address = forms.CharField(max_length=255, required=True, label=_("Full address"),widget=forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'آدرس*'}))
    phone_number = forms.CharField(max_length=20,required=False,validators=[phone_number_validator], label=_("Phone number"),widget=forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'تلفن'}))

    description = forms.CharField(max_length=500, label=_("Description"), required=False, widget= forms.TextInput(attrs={"class":tailwind_classes,"placeholder":'توضیحات'})) 


    shipping_method = forms.ChoiceField(
        choices=SHIPPING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'hidden peer'
        }),
        initial='post',
        required=True
    )