from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class ParentProduct(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("parent product name"))
    category = models.ForeignKey('ProductCategory', on_delete=models.PROTECT, blank=True, null=True, related_name='product_parents', verbose_name=_("category"))
    brand = models.ForeignKey('Brand', on_delete=models.PROTECT, blank=True, null=True, related_name='product_parents', verbose_name=_("brand"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("slug"))
    
    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)

class Product(models.Model):
    parent_name = models.ForeignKey('ParentProduct', on_delete=models.PROTECT, related_name='products', verbose_name=_("product name"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("slug"))
    
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_("price (Toman)"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name=_("discounted price (Toman)"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("stock"))

    is_available = models.BooleanField(default=True, verbose_name=_("is available"))
    is_amazing = models.BooleanField(default=False, verbose_name=_("is amazing?"))
    is_best_selling = models.BooleanField(default=False, verbose_name=_("is best selling?"))

    color = models.ManyToManyField('Color', blank=True, verbose_name=_("colors"))
    attribute_values = models.ManyToManyField('AttributeValue', verbose_name=_("attribute values"))


    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products"  )

    def clean(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({'discount_price': _("Discount price must be less than the original price.")})


    def __str__(self):
        return f'{self.id}:{self.parent_name}'
    
    def get_absolute_url(self):
        return reverse('products:post_redirect', kwargs={'pk': self.pk})
    
    @property
    def full_name(self):
        base_name = f'{self.parent_name.category} {self.parent_name.brand} مدل {self.parent_name.name} '
        storage_value_obj = self.attribute_values.filter(attribute__name='حافظه داخلی').first()
        ram_value_obj = self.attribute_values.filter(attribute__name='رم').first()
        register_value_obj = self.attribute_values.filter(attribute__name='وضعیت رجیستر').first()
        
        if storage_value_obj:
            base_name += f'ظرفیت {storage_value_obj.value} گیگابایت '
        if ram_value_obj:
            base_name += f'رم {ram_value_obj.value} گیگابایت '
        if register_value_obj:
            base_name += f'({register_value_obj.value}) '
        return base_name.strip()
    
    def save(self, *args, **kwargs):
        if not self.slug:
            storage_value_obj = self.attribute_values.filter(attribute__name='حافظه داخلی').first()
            ram_value_obj = self.attribute_values.filter(attribute__name='رم').first()
            slug_text = {self.parent_name.name}-{storage_value_obj.value if storage_value_obj else ''}-{ram_value_obj.value if ram_value_obj else ''}
            self.slug = slugify(slug_text)

        self.is_available = self.stock > 0
        super().save(*args, **kwargs)



def product_image_upload_to(instance, filename):
    return f'products/{instance.parent_product.slug}/{filename}'

class ProductImage(models.Model):
    parent_product = models.ForeignKey(ParentProduct, on_delete=models.CASCADE, related_name='images', verbose_name=_("parent product"))
    image = models.ImageField(upload_to=product_image_upload_to, verbose_name=_("product image"))
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("alt text"))

    def __str__(self):
        return f"Image for {self.parent_product.name}"

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ['-id']

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("category name"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("category code"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("slug"))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name=_("parent category"))


    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('product category')
        verbose_name_plural = _('product categories')
        ordering = ['name']

class Attribute(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("attribute name"))
    categories = models.ManyToManyField(ProductCategory, related_name='attributes', verbose_name=_("related categories"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('attribute')
        verbose_name_plural = _('attributes')
        ordering = ['name']

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name=_("attribute"))
    value = models.CharField(max_length=255, verbose_name=_("attribute value"))
    def __str__(self):
        return f"{self.attribute.name}: {self.value}"

    class Meta:
        verbose_name = _('attribute value')
        verbose_name_plural = _('attribute values')
        unique_together = ('value', 'attribute')
        ordering = ['attribute']

class Color(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("color name"))
    hex_code = models.CharField(max_length=7, verbose_name=_("hex code"))
    def __str__(self):
        return self.name
    
class Brand(models.Model):
    name = models.CharField(max_length=50, verbose_name=_("brand"))
    code = models.CharField(max_length=50, unique=True, verbose_name=_("brand code"))
    category = models.ManyToManyField(ProductCategory, related_name='brands', verbose_name=_("related categories"))

    def __str__(self):
        return self.name