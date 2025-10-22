from django import forms
from .models import Comments
from django.utils.translation import gettext_lazy as _

class CommentForm(forms.ModelForm):
    class Meta: 
        model = Comments
        fields = ['title', 'content', 'rating', 'is_recommend']
        labels = {
            'title': _("Title"),
            'content': _("Comment"),
            'rating': _("Rating"),
            'is_recommend': _("Do you recommend this product?"),
        }
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'عنوان',
                'class': 'tailwind-input w-full',
                'name': 'title' 
            }),
            'content': forms.Textarea(attrs={
                'placeholder': 'متن دیدگاه',
                'class': 'h-24 tailwind-input w-full',
                'name': 'content'
            }),
            
            'rating': forms.HiddenInput(attrs={
                'id': 'rating-value',
                'name': 'rating'
            }),
        }