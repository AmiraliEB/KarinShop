from collections import defaultdict
import uuid
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.db.models.signals import m2m_changed, post_save, post_delete 
from django.dispatch import receiver
from django.utils.text import slugify

User = get_user_model()

class ParentProduct(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("parent product name"))
    category = models.ForeignKey('ProductCategory', on_delete=models.PROTECT, blank=True, null=True, related_name='product_parents', verbose_name=_("category"))
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT, blank=True, null=True, related_name='product_parents', verbose_name=_("brand"))

    specification_values = models.ManyToManyField(
        'AttributeValue', 
        related_name='parent_products', 
        verbose_name=_("shared specifications"),
        blank=True,
        limit_choices_to={'attribute__show_in_specifications': True,'attribute__is_variant_defining': False}
    )

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def __str__(self):
        return self.name
    @property
    def grouped_specifications(self):
        if hasattr(self, 'sorted_attribute_values'):
            values_list = self.sorted_attribute_values
        else:
            values_list = self.specification_values.select_related(
                'attribute__attribute_category'
            ).order_by('attribute__attribute_category__sort_order')

        grouped_attributes = defaultdict(list)
        for value_obj in values_list:
            category = value_obj.attribute.attribute_category
            grouped_attributes[category].append(value_obj)
        
        return dict(grouped_attributes)
    
class Product(models.Model):
    parent_product = models.ForeignKey('ParentProduct', on_delete=models.PROTECT, related_name='products', verbose_name=_("product name"))
    
    _full_name = models.CharField(max_length=500, blank=True, verbose_name=_("Full Name (Cached)"))

    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_("price (Toman)"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name=_("discounted price (Toman)"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("stock"))

    is_available = models.BooleanField(default=True, verbose_name=_("is available"))
    is_amazing = models.BooleanField(default=False, verbose_name=_("is amazing?"))
    is_best_selling = models.BooleanField(default=False, verbose_name=_("is best selling?"))

    attribute_values = models.ManyToManyField('AttributeValue', verbose_name=_("attribute values"),limit_choices_to={'attribute__is_variant_defining': True})


    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products"  )

    def clean(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({'discount_price': _("Discount price must be less than the original price.")})


    def __str__(self):
        return self.full_name if self._full_name else f'Product {self.id}'
    
    def get_absolute_url(self):
        return reverse('products:post_redirect', kwargs={'pk': self.pk})
    @property
    def full_name(self):
        return self._full_name
    
    def _generate_full_name(self):
        base_name = f'{self.parent_product.category} {self.parent_product.brand} {self.parent_product.name}'
        
        product_category = self.parent_product.category
        product_brand = self.parent_product.brand

        if not product_category:
            return base_name
        

        applicable_rules_query = Q(
            attributerule__category=product_category,
            attributerule__brand=product_brand
        ) | Q(
            attributerule__category=product_category,
            attributerule__brand__isnull=True
        )

        main_feature_attributes = Attribute.objects.filter(
            applicable_rules_query,
            attributerule__is_main_feature=True
        ).distinct() 
        main_specification_values = self.parent_product.specification_values.filter(
            attribute__in=main_feature_attributes
        ).select_related('attribute')
        main_attribute_values = self.attribute_values.filter(
            attribute__in=main_feature_attributes
        ).select_related('attribute')
        main_values = main_attribute_values | main_specification_values
        final_parts = list()
        for attribute_value_obj in main_values:
            attribute_value = attribute_value_obj.value
            final_parts.append(attribute_value)


        return f"{base_name} {' '.join(final_parts)}".strip()
        
    
    def save(self, *args, **kwargs):
        self.is_available = self.stock > 0
        super().save(*args, **kwargs)
        
        new_full_name = self._generate_full_name()
        if self._full_name != new_full_name:
            self._full_name = new_full_name
            super().save(update_fields=['_full_name'])


def product_image_upload_to(instance, filename):
    return f'products/{slugify(instance.parent_product.name)}/{filename}'

class ProductImage(models.Model):
    parent_product = models.ForeignKey(ParentProduct, on_delete=models.CASCADE, related_name='images', verbose_name=_("parent product"))
    image = models.ImageField(upload_to=product_image_upload_to, verbose_name=_("product image"))
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("alt text"))
    is_main_image = models.BooleanField(default=False, verbose_name=_("is main image?"))
    def __str__(self):
        return f"Image for {self.parent_product.name}"

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ['-id']
    
    def clean(self):
        if self.parent_product is None:
            raise ValidationError({'parent_product': _("Parent product must be set for the image.")})
        if not self.image:
            raise ValidationError({'image': _("Image file must be provided.")})
    
    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        constraints = [
            models.UniqueConstraint(
                fields=['parent_product'], 
                condition=Q(is_main_image=True),
                name='unique_main_image_per_product',
            )
        ]

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("category name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("category code"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name=_("parent category"))

    attribute_categories = models.ManyToManyField(
        'AttributeCategory',
        blank=True,
        verbose_name=_("attribute categories")
    )


    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')
        ordering = ['name']

class Attribute(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("attribute name"))
    product_category = models.ManyToManyField(ProductCategory, related_name='attributes', verbose_name=_("related categories"),through='AttributeRule')
    
    attribute_category = models.ForeignKey(
        'AttributeCategory',
        related_name='attributes',
        on_delete=models.PROTECT,
        null=True,
        blank=False,
        verbose_name=_("attribute category")
    )
    is_variant_defining = models.BooleanField(
        default=False, 
        verbose_name=_("Is this a variant-defining attribute?")
    )
    show_in_specifications = models.BooleanField(_("Show in specifications in detail page?"),default=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('attribute')
        verbose_name_plural = _('attributes')
        ordering = ['attribute_category']

class AttributeRule(models.Model):
    attribute = models.ForeignKey("Attribute", verbose_name=_("attribute"), on_delete=models.CASCADE)
    category = models.ForeignKey("ProductCategory", verbose_name=_("category"), on_delete=models.CASCADE)
    brand = models.ForeignKey("Brand", verbose_name=_("brand"), on_delete=models.CASCADE,blank=True,null=True)

    is_main_feature = models.BooleanField(default=False,verbose_name=_("Show in product tite?"))

    class Meta:
        verbose_name = _("Attribute Rule")
        verbose_name_plural = _("Attribute Rules")
        constraints = [
            models.UniqueConstraint(
                fields=['attribute', 'category', 'brand'], 
                name='unique_attribute_category_brand'
            ),
            models.UniqueConstraint(
                fields=['attribute', 'category'], 
                condition=Q(brand__isnull=True), 
                name='unique_attribute_category_when_brand_is_null'
            )
        ]
        
        
    def __str__(self):
        if self.brand:
            return f"{self.attribute.name} برای {self.category.name} {self.brand.name}"
        return f"{self.attribute.name} برای {self.category.name}"
    
class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name=_("attribute"))
    value = models.CharField(max_length=255, verbose_name=_("attribute value"))
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        verbose_name = _('attribute value')
        verbose_name_plural = _('attribute values')
        unique_together = ('value', 'attribute')
        ordering = ['attribute__id']

class AttributeCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("category name"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("sort order"))
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('attribute category')
        verbose_name_plural = _('attribute categories')
        ordering = ['id']

class Brand(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("brand"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("brand code"))
    category = models.ManyToManyField(ProductCategory, related_name='brands', verbose_name=_("related categories"))

    def __str__(self):
        return self.name




class Comments(models.Model):
    # comment should pe linked to parent product
    parent_product = models.ForeignKey(ParentProduct, on_delete=models.CASCADE, related_name='comments', verbose_name=_("product"))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments', verbose_name=_("user"))
    
    title = models.CharField(_("title"), max_length=200)
    content = models.TextField(verbose_name=_("comment content"))
    rating = models.PositiveSmallIntegerField(verbose_name=_("rating"),validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    is_recommend = models.BooleanField(default=None, verbose_name=_("   "), null=True, blank=True)
    is_approved = models.BooleanField(default=False, verbose_name=_("is approved by admin?"))
    
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")
        ordering = ['-datetime_created'] 

    def __str__(self):
        return f"Comment by {self.user} on {self.parent_product}"
    


@receiver(m2m_changed, sender=Product.attribute_values.through)
def update_full_name_on_m2m_change(sender, instance, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        new_full_name = instance._generate_full_name()
        if instance._full_name != new_full_name:
            instance._full_name = new_full_name
            instance.save(update_fields=['_full_name'])

@receiver([post_save, post_delete], sender=AttributeRule)
def update_product_names_on_rule_change(sender, instance, **kwargs):
    category = instance.category
    brand = instance.brand
    if brand:
        affected_parent_products = ParentProduct.objects.filter(category=category, brand=brand)
    else:
        affected_parent_products = ParentProduct.objects.filter(category=category)
    affected_products = Product.objects.filter(
        parent_product__in=affected_parent_products
    ).iterator()
    for product in affected_products:
        new_full_name = product._generate_full_name()
        if product._full_name != new_full_name:
            product._full_name = new_full_name
            product.save(update_fields=['_full_name'])