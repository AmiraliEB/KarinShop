from django.db import models
from django.utils.text import slugify

#TODO: Add brand and category field
class Product(models.Model):
    name = models.CharField(max_length=255,verbose_name="نام محصول")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="اسلاگ", allow_unicode=True)
    price = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="قیمت (تومان)")
    discount_price = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True, verbose_name="قیمت با تخفیف (تومان)")
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")

    is_amazing = models.BooleanField(default=False, verbose_name="محصول شگفت‌انگیز؟")
    is_available = models.BooleanField(default=True, verbose_name="موجود است؟")
    is_best_selling = models.BooleanField(default=False, verbose_name="پرفروش است؟")

    datetime_created = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    datetime_modified = models.DateTimeField(auto_now=True, verbose_name="تاریخ آخرین ویرایش")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        if self.stock == 0:
            self.is_available = False
        super().save(*args, **kwargs)
    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'
        ordering = ['name']



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
