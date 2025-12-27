from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django import forms
from .models import Comments, ParentProduct, Product
from django.utils.translation import gettext_lazy as _


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ["title", "content", "rating", "is_recommend"]
        labels = {
            "title": _("Title"),
            "content": _("Comment"),
            "rating": _("Rating"),
            "is_recommend": _("Do you recommend this product?"),
        }
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "عنوان", "class": "tailwind-input w-full", "name": "title"}),
            "content": forms.Textarea(
                attrs={"placeholder": "متن دیدگاه", "class": "h-24 tailwind-input w-full", "name": "content"}
            ),
            "rating": forms.HiddenInput(attrs={"id": "rating-value", "name": "rating"}),
            "is_recommend": forms.HiddenInput(attrs={"id": "recommend-value", "name": "is_recommend"}),
        }

    def save(self, request, product, commit=True):
        comment = super().save(commit=False)
        comment.user = request.user
        comment.parent_product = product.parent_product

        if self.cleaned_data.get("is_recommend") is None:
            comment.is_recommend = comment.rating >= 3

        if commit:
            comment.save()
        return comment


class ProductImageFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        if any(self.errors):
            return

        count_is_main = 0
        count_active_images = 0
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):

                count_active_images += 1

                if form.cleaned_data.get("is_main_image"):
                    count_is_main += 1
            if form.cleaned_data.get("DELETE", False) and form.cleaned_data.get("is_main_image"):
                raise ValidationError(_("نمی‌توانید عکس اصلی را حذف کنید. لطفاً ابتدا عکس اصلی دیگری انتخاب کنید."))

        if count_is_main > 1:
            raise ValidationError(_('شما فقط می‌توانید یک عکس را به عنوان "عکس اصلی" انتخاب کنید.'))

        if count_is_main == 0:
            raise ValidationError(_("لطفاً یکی از عکس‌ها را به عنوان عکس اصلی انتخاب کنید."))

        if count_active_images < 5:
            raise ValidationError(
                _(
                    (
                        f"شما باید حداقل ۴ عکس آپلود کنید. (در حال حاضر {count_active_images} عکس دارید) اگر می‌خواهید "
                        f"عکسی را حذف کنید، لطفاً ابتدا عکس جدیدی اضافه کنید."
                    )
                )
            )


class ProductFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        if any(self.errors):
            return

        seen_combinations = []

        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get("DELETE", False):

                selected_values = form.cleaned_data.get("attribute_values")
                if not selected_values:
                    continue

                seen_attributes = set()

                for value in selected_values:
                    parent_attr = value.attribute

                    if not parent_attr.allow_multiple_values:
                        if parent_attr.id in seen_attributes:
                            form.add_error(
                                "attribute_values",
                                _(
                                    (
                                        f"شما نمی‌توانید برای ویژگی «{parent_attr.name}» چند مقدار انتخاب کنید."
                                        f"اگر میخواهید ویژگی ای را چند بار تکرار کنید در جدول ویژگی گزینه «امکان انتخاب"
                                        f"چند مقدار همزمان در واریانت» را فعال کنید."
                                    )
                                ),
                            )

                    seen_attributes.add(parent_attr.id)

                current_ids = sorted([attr.id for attr in selected_values])
                current_combination = tuple(current_ids)

                if len(current_combination) < 3:
                    form.add_error("attribute_values", _("حداقل ۳ ویژگی انتخاب کنید."))

                if current_combination in seen_combinations:
                    raise ValidationError(_("این ترکیب دقیقاً تکراری است."))

                seen_combinations.append(current_combination)


class ParentProductAdminForm(forms.ModelForm):
    class Meta:
        model = ParentProduct
        fields = "__all__"

    def clean_specification_values(self):
        selected_values = self.cleaned_data.get("specification_values")

        if not selected_values:
            return selected_values

        seen_attributes = set()

        for value in selected_values:
            parent_attr = value.attribute
            if not getattr(parent_attr, "allow_multiple_values", False):
                if parent_attr.id in seen_attributes:
                    raise ValidationError(
                        _(
                            (
                                f"شما نمی‌توانید برای ویژگی «{parent_attr.name}» چند مقدار انتخاب کنید. اگر میخواهید"
                                f"ویژگی ای را چند بار تکرار کنید در جدول ویژگی گزینه"
                                f"«امکان انتخاب چند مقدار همزمان در واریانت» را فعال کنید."
                            )
                        )
                    )

            seen_attributes.add(parent_attr.id)

        return selected_values


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()

        selected_values = cleaned_data.get("attribute_values")
        parent = cleaned_data.get("parent_product")

        if not selected_values or not parent:
            return cleaned_data

        seen_attributes = set()

        for value in selected_values:
            parent_attr = value.attribute

            if not getattr(parent_attr, "allow_multiple_values", False):
                if parent_attr.id in seen_attributes:
                    self.add_error(
                        "attribute_values",
                        _(
                            (
                                f"شما نمی‌توانید برای ویژگی «{parent_attr.name}» چند مقدار انتخاب کنید. اگر می‌خواهید"
                                f"ویژگی‌ای را چند بار تکرار کنید در جدول ویژگی گزینه"
                                f"«امکان انتخاب چند مقدار همزمان در واریانت» را فعال کنید."
                            )
                        ),
                    )

            seen_attributes.add(parent_attr.id)

        if self.errors:
            return cleaned_data

        current_ids = sorted([attr.id for attr in selected_values])
        current_combination = tuple(current_ids)

        if len(current_combination) < 3:
            self.add_error("attribute_values", _("حداقل ۳ ویژگی انتخاب کنید."))

        siblings = Product.objects.filter(parent_product=parent)

        if self.instance.pk:
            siblings = siblings.exclude(pk=self.instance.pk)

        for sibling in siblings:
            sibling_ids = sorted(list(sibling.attribute_values.values_list("id", flat=True)))
            sibling_combination = tuple(sibling_ids)

            if current_combination == sibling_combination:
                raise ValidationError(_("این ترکیب دقیقاً تکراری است و قبلاً برای محصول دیگری ثبت شده است."))

        return cleaned_data
