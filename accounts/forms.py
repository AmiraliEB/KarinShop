from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm, LoginForm, ResetPasswordForm, ResetPasswordKeyForm
from django import forms
from .models import CustomUser
from allauth.account.utils import get_adapter,filter_users_by_email
from allauth.account import app_settings

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['login'].widget = forms.TextInput(
            attrs={
                'class': "block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-alltext-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':"ایمیل"})
        self.fields['password'].widget = forms.PasswordInput(
            attrs={
                'class': "block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-alltext-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':'رمز عبور'})
class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget = forms.TextInput(
            attrs={
                'class': "block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-alltext-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':"ایمیل"})
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={
                'class': "block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-alltext-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':'رمز عبور'})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={
                'class': "block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-alltext-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':'رمز عبور (تکرار)'})

class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget = forms.TextInput(
            attrs={
                'class': "block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-gray-400  sm:text-sm/6 transition-alltext-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':"ایمیل"})
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        email = get_adapter().clean_email(email)

        # 2. کاربران را بدون فیلتر is_active پیدا می‌کنیم.
        users = filter_users_by_email(email, is_active=None)
        
        # 3. متغیر self.users را برای استفاده در متد save مقداردهی می‌کنیم.
        #    این بخش بسیار حیاتی است که در کد قبلی فراموش شده بود.
        self.users = [user for user in users if user.is_active]

        # 4. حالا منطق بررسی وضعیت را اجرا می‌کنیم.
        if not users:
            # اگر هیچ کاربری (چه فعال و چه غیرفعال) پیدا نشد،
            # منطق پیش‌فرض allauth را اجرا می‌کنیم.
            if not app_settings.PREVENT_ENUMERATION:
                raise get_adapter().validation_error("unknown_email")
        
        elif not self.users:
            # اگر کاربری پیدا شد (users خالی نیست)، اما هیچ‌کدام فعال نبودند (self.users خالی است)
            raise get_adapter().validation_error("inactive_account")
        
        # اگر همه چیز درست بود، ایمیل اصلی را برمی‌گردانیم.
        return self.cleaned_data["email"]

        
class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget = forms.PasswordInput(
            attrs={
                'class': "p-3 w-full sm:text-sm/6 text-base appearance-none text-gray-800 dark:text-gray-100",
                'placeholder':"پسورد جدید"})
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={
                'class': "p-3 w-full sm:text-sm/6 text-base appearance-none text-gray-800 dark:text-gray-100",
                'placeholder':"تکرار رمز عبور*"})
        
    