from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
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
            'is_recommend': forms.HiddenInput(attrs={
                'id': 'recommend-value',
                'name': 'is_recommend'
            })
        }

class ProductImageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        count_is_main = 0
        count_active_images = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):

                count_active_images += 1

                if form.cleaned_data.get('is_main_image'):
                    count_is_main += 1
            if form.cleaned_data.get('DELETE', False) and form.cleaned_data.get('is_main_image'):
                raise ValidationError('نمی‌توانید عکس اصلی را حذف کنید. لطفاً ابتدا عکس اصلی دیگری انتخاب کنید.')

        if count_is_main > 1:
            raise ValidationError('شما فقط می‌توانید یک عکس را به عنوان "عکس اصلی" انتخاب کنید.')
        
        if count_is_main == 0:
            raise ValidationError('لطفاً یکی از عکس‌ها را به عنوان عکس اصلی انتخاب کنید.')
        
        if count_active_images < 4:
            raise ValidationError(f'شما باید حداقل ۴ عکس آپلود کنید. (در حال حاضر {count_active_images} عکس دارید) اگر می‌خواهید عکسی را حذف کنید، لطفاً ابتدا عکس جدیدی اضافه کنید.')