from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

#TODO: Add brand model
class Product(models.Model):
    PRODUCT_TYPE_CHOICES = (
        ('PARENT', _('parent')),
        ('CHILD', _('child')),
    )

    product_type = models.CharField(
        _("product type"),
        max_length=10,
        choices=PRODUCT_TYPE_CHOICES,
        default='CHILD'
    )

    parent = models.ForeignKey(
    'self',
    on_delete=models.CASCADE,
    null=True,
    blank=True,
    related_name='children',
    verbose_name=_("parent product")
    )

    name = models.CharField(max_length=255,verbose_name=_("product name"))
    category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, blank=True, null=True, related_name='products', verbose_name=_("category"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("slug"), allow_unicode=True)
    
    fixed_attribute = models.ManyToManyField('AttributeValue', blank=True, verbose_name=_("fixed attributes"))
    is_variable = models.BooleanField(default=False, verbose_name=_("product has color?"))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products"  )
        ordering = ['name']

class ProductVariant(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='variants', verbose_name=_("product"))
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name=_("price (Toman)"))
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name=_("discounted price (Toman)"))
    stock = models.PositiveIntegerField(default=0, verbose_name=_("stock"))

    is_available = models.BooleanField(default=True, verbose_name=_("is available"))
    is_amazing = models.BooleanField(default=False, verbose_name=_("is amazing?"))
    is_best_selling = models.BooleanField(default=False, verbose_name=_("is best selling?"))

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name=_("creation date"))
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name=_("last modified date"))

    variant_attributes = models.ManyToManyField('AttributeValue', verbose_name=_("variant attributes"))

    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.is_available = False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('product variant')
        verbose_name_plural = _('product variants')


    def __str__(self):
        variant_name = " / ".join([str(attr.value) for attr in self.variant_attributes.all()])
        return f"{self.product.name} ({variant_name})"

def product_image_upload_to(instance, filename):
    return f'products/{instance.product.slug}/{filename}'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name=_("product"))
    image = models.ImageField(upload_to=product_image_upload_to, verbose_name=_("product image"))
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("alt text"))

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = _('product image')
        verbose_name_plural = _('product images')
        ordering = ['-id']

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name=_("category name"))
    slug = models.SlugField(max_length=255, unique=True, verbose_name=_("slug"), allow_unicode=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name=_("parent category"))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
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
