from django.db import models
from django.utils.text import slugify

#TODO: Add brand model
class Product(models.Model):
    name = models.CharField(max_length=255,verbose_name="نام محصول")
    category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, blank=True, null=True, related_name='products', verbose_name="دسته‌بندی")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="اسلاگ", allow_unicode=True)
    
    fixed_attribute = models.ManyToManyField('AttributeValue', blank=True, verbose_name="ویژگی‌های ثابت")
    is_variable = models.BooleanField(default=False, verbose_name="آیا محصول متغیر است؟")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="تاریخ آخرین ویرایش")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['name']

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="محصول")
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت (تومان)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="قیمت با تخفیف (تومان)")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")

    is_available = models.BooleanField(default=True, verbose_name="موجود است؟")
    is_amazing = models.BooleanField(default=False, verbose_name="محصول شگفت‌انگیز؟")
    is_best_selling = models.BooleanField(default=False, verbose_name="پرفروش است؟")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="تاریخ آخرین ویرایش")

    variant_attributes = models.ManyToManyField('AttributeValue', verbose_name="ویژگی‌های این نسخه")

    def __str__(self):
        return f"{self.product.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if self.stock == 0:
            self.is_available = False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'واریانت محصول'
        verbose_name_plural = 'واریانت‌های محصولات'


    def __str__(self):
        variant_name = " / ".join([str(attr.value) for attr in self.variant_attributes.all()])
        return f"{self.product.name} ({variant_name})"

def product_image_upload_to(instance, filename):
    return f'products/{instance.product.slug}/{filename}'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول")
    image = models.ImageField(upload_to=product_image_upload_to, verbose_name="تصویر محصول")
    alt_text = models.CharField(max_length=255, blank=True, null=True, verbose_name="متن جایگزین تصویر")

    def __str__(self):
        return f"Image for {self.product.name}"

    class Meta:
        verbose_name = 'تصویر محصول'
        verbose_name_plural = 'تصاویر محصولات'
        ordering = ['-id']

class ProductCategory(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="اسلاگ", allow_unicode=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='children', verbose_name="دسته‌بندی والد")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'دسته‌بندی محصول'
        verbose_name_plural = 'دسته‌بندی‌های محصولات'
        ordering = ['name']

class Attribute(models.Model):
    name = models.CharField(max_length=255, verbose_name="نام ویژگی")
    categories = models.ManyToManyField(ProductCategory, related_name='attributes', verbose_name="دسته‌بندی‌های مرتبط")
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ویژگی'
        verbose_name_plural = 'ویژگی‌ها'
        ordering = ['name']

class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values', verbose_name="ویژگی")
    value = models.CharField(max_length=255, verbose_name="مقدار ویژگی")

    def __str__(self):
        return f"{self.attribute.name}: {self.value} for {self.product.name}"

    class Meta:
        verbose_name = 'مقدار ویژگی محصول'
        verbose_name_plural = 'مقادیر ویژگی‌های محصولات'
        unique_together = ('value', 'attribute')
        ordering = ['attribute']
