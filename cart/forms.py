from django import forms

class CartAddPrproductForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].widget = forms.NumberInput(
            attrs={
                'class': 'custom-input mr-4 text-lg bg-transparent',
                'id': 'customInput'
            })
    QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]
    quantity = forms.TypedChoiceField(choices=QUANTITY_CHOICES, coerce=int)

