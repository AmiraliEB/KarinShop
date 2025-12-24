<div dir="rtl">

# 🛍️ فروشگاه اینترنتی کارین‌شاپ (KarinShop)

<p align="center">
  <strong>یک پلتفرم فروشگاهی پیشرفته با معماری مدرن Django و قابلیت مدیریت محصولات متغیر</strong>
</p>

<p align="center">
  <a href="#-درباره-پروژه">درباره پروژه</a> •
  <a href="#-ویژگی‌های-کلیدی">ویژگی‌ها</a> •
  <a href="#-تکنولوژی‌های-استفاده-شده">تکنولوژی‌ها</a> •
  <a href="#-راه‌اندازی-با-داکر">نصب و اجرا</a> •
  <a href="#-لیست-متغیرهای-محیطی">تنظیمات</a>
</p>

---

## 📝 درباره پروژه

**کارین‌شاپ** یک سیستم فروشگاه اینترنتی متن‌باز (Open Source) است که با استفاده از فریم‌ورک **Django** توسعه داده شده است. برخلاف فروشگاه‌های ساده، این پروژه بر روی **مدیریت پیشرفته محصولات** (Product Variants) تمرکز دارد و به مدیران اجازه می‌دهد محصولات با ویژگی‌های متغیر (مانند رنگ، حافظه، سایز) را به صورت پویا تعریف کنند.

این پروژه برای پرفورمنس بالا بهینه‌سازی شده، از **HTMX** برای تعاملات بدون رفرش صفحه استفاده می‌کند و کاملاً **Dockerize** شده است.

## ✨ ویژگی‌های کلیدی

### 📦 مدیریت پیشرفته محصولات
* **سیستم Parent/Child:** معماری پیشرفته برای مدیریت واریانت‌ها (محصول مادر و زیرمجموعه‌ها).
* **ویژگی‌های پویا (Dynamic Attributes):** امکان تعریف ویژگی‌های دلخواه (رنگ، سایز و...) و انتساب آن‌ها به دسته‌بندی‌های خاص.
* **مشخصات فنی:** تولید خودکار جدول مشخصات فنی بر اساس ویژگی‌های محصول.
* **گالری تصاویر:** مدیریت تصویر اصلی و گالری تصاویر برای هر واریانت.
* **برند و دسته‌بندی:** سیستم دسته‌بندی تو در تو و مدیریت برندها.
* **نظرات و امتیازدهی:** سیستم ثبت دیدگاه و امتیاز با قابلیت تایید توسط ادمین و پیشنهاد خرید.

### 🛒 سبد خرید و سفارشات
* **سبد خرید هیبریدی:** ذخیره سبد خرید در Session برای کاربران مهمان و انتقال خودکار به دیتابیس پس از ورود به حساب کاربری.
* **تعاملات زنده (HTMX):** افزودن، حذف و تغییر تعداد محصول در سبد خرید بدون رفرش صفحه.
* **سیستم تخفیف:** پشتیبانی از کوپن‌های تخفیف (درصدی و مبلغ ثابت) با محدودیت تعداد و زمان.
* **محاسبه هزینه ارسال:** انتخاب روش ارسال (پست، تیپاکس و...) و محاسبه هزینه در فاکتور نهایی.
* **مدیریت سفارش:** پیگیری وضعیت سفارش (در انتظار، تایید شده، ارسال شده).

### 👤 کاربران و احراز هویت
* **ثبت‌نام و ورود:** استفاده از ایمیل به عنوان شناسه اصلی (Custom User Model).
* **ورود اجتماعی (Social Auth):** قابلیت ورود با حساب Google و GitHub.
* **مدیریت پروفایل:** پنل کاربری برای مدیریت اطلاعات شخصی و آدرس‌های ارسال.
* **تاریخ شمسی:** پشتیبانی کامل از تاریخ و تقویم شمسی در سراسر سیستم.

## 🛠 تکنولوژی‌های استفاده شده

| بخش | تکنولوژی |
| :--- | :--- |
| **زبان و فریم‌ورک** | [![Python][python-badge]][python-url] [![Django][django-badge]][django-url] |
| **پایگاه داده** | [![PostgreSQL][postgresql-badge]][postgresql-url] |
| **فرانت‌اند** | [![HTML5][html-badge]][html-url] [![Tailwind CSS][tailwind-badge]][tailwind-url] [![HTMX][htmx-badge]][htmx-url] [![Alpine.js][alpine-badge]][alpine-url] |
| **زیرساخت** | [![Docker][docker-badge]][docker-url] [![Nginx][nginx-badge]][nginx-url] [![Gunicorn][gunicorn-badge]][gunicorn-url] |

[python-badge]: https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white
[python-url]: https://www.python.org/
[django-badge]: https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white
[django-url]: https://www.djangoproject.com/
[postgresql-badge]: https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white
[postgresql-url]: https://www.postgresql.org/
[html-badge]: https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white
[html-url]: https://developer.mozilla.org/en-US/docs/Web/HTML
[tailwind-badge]: https://img.shields.io/badge/Tailwind_CSS-38B2AC?style=for-the-badge&logo=tailwind-css&logoColor=white
[tailwind-url]: https://tailwindcss.com/
[htmx-badge]: https://img.shields.io/badge/HTMX-3D5875?style=for-the-badge&logo=htmx&logoColor=white
[htmx-url]: https://htmx.org/
[alpine-badge]: https://img.shields.io/badge/Alpine.js-8BC0D0?style=for-the-badge&logo=alpine.js&logoColor=white
[alpine-url]: https://alpinejs.dev/
[docker-badge]: https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white
[docker-url]: https://www.docker.com/
[nginx-badge]: https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white
[nginx-url]: https://nginx.org/
[gunicorn-badge]: https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white
[gunicorn-url]: https://gunicorn.org/

## 🚀 راه‌اندازی با داکر (روش پیشنهادی)

ساده‌ترین روش برای اجرای پروژه استفاده از داکر است.

**پیش‌نیازها:**
* Docker و Docker Compose

**مراحل نصب:**

۱. مخزن را کلون کنید:
   ```bash
   git clone [https://github.com/your-username/karinshop.git](https://github.com/your-username/karinshop.git)
   cd karinshop

```

۲. فایل متغیرهای محیطی را بسازید:

```bash
cp .env.example .env

```

*(سپس فایل `.env` را باز کرده و مقادیر مورد نیاز را تنظیم کنید. به بخش [متغیرهای محیطی](https://www.google.com/search?q=%23-%D9%84%DB%8C%D8%B3%D8%AA-%D9%85%D8%AA%D8%BA%DB%8C%D8%B1%D9%87%D8%A7%DB%8C-%D9%85%D8%AD%DB%8C%D8%B7%DB%8C) مراجعه کنید.)*

۳. پروژه را بیلد و اجرا کنید:

```bash
docker-compose up --build -d

```

۴. مایگریشن‌ها را اعمال کنید و یک سوپریوزر بسازید:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser

```

اکنون پروژه در آدرس `http://localhost:8000` در دسترس است.

## ⚙️ راه‌اندازی دستی (محیط توسعه)

۱. یک محیط مجازی بسازید و فعال کنید:

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

```

۲. وابستگی‌ها را نصب کنید:

```bash
pip install -r requirements.txt

```

۳. تنظیمات دیتابیس را در فایل `.env` انجام دهید (می‌توانید از SQLite برای تست استفاده کنید یا Postgres نصب کنید).

۴. دستورات اولیه را اجرا کنید:

```bash
python backend/manage.py migrate
python backend/manage.py runserver

```

## 🔑 لیست متغیرهای محیطی

مقادیر زیر باید در فایل `.env` تنظیم شوند:

```ini
DEBUG=True
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1

# تنظیمات دیتابیس
POSTGRES_DB=postgres_db
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=password
DB_HOST=db_host
DB_PORT=000

# تنظیمات ایمیل (برای فراموشی رمز عبور و...)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=000
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

```

## 🧪 اجرای تست‌ها

این پروژه شامل تست‌های خودکار است که با `pytest` نوشته شده‌اند. برای اجرای تست‌ها:

```bash
# در محیط داکر
docker-compose exec web pytest

# در محیط دستی
pytest

```

## 🗺 نقشه راه آینده (Roadmap)

* [ ] اتصال به درگاه پرداخت بانکی (Zarinpal/NextPay)
* [ ] پیاده‌سازی سیستم کشینگ (Redis) برای بهبود سرعت
* [ ] سیستم اطلاع‌رسانی پیامکی (SMS)
* [ ] تکمیل داشبورد گزارش‌گیری برای ادمین