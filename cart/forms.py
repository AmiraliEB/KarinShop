from django import forms

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