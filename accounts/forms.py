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
                'class': "peer inline-block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':" "
            })
        self.fields['password'].widget = forms.PasswordInput(
            attrs={
                'class': "peer w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':' ',
                'id' : 'passwordInput'
            })
class CustomSignupForm(SignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget = forms.TextInput(
            attrs={
                'class': "peer inline-block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':" "
            })
        self.fields['password1'].widget = forms.PasswordInput(
            attrs={
                'class': "peer w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':' '
            })
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={
                'class': "peer w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':' '
            })

class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget = forms.TextInput(
            attrs={
                'class': "peer inline-block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':" "
            })
    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        email = get_adapter().clean_email(email)

        users = filter_users_by_email(email, is_active=None)
        
        self.users = [user for user in users if user.is_active]

        if not users:
            if not app_settings.PREVENT_ENUMERATION:
                raise get_adapter().validation_error("unknown_email")
        
        elif not self.users:
            raise get_adapter().validation_error("inactive_account")
        
        return self.cleaned_data["email"]

        
class CustomResetPasswordKeyForm(ResetPasswordKeyForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].widget = forms.PasswordInput(
            attrs={
                'class': "peer w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':" ",
                'id' : 'passwordInput'
            })
        self.fields['password2'].widget = forms.PasswordInput(
            attrs={
                'class': "peer w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder':" ",
                'id' : 'confirmPassword'
            })
        
class ResendConfirmationEmailForm(forms.Form):

    email = forms.EmailField(
        label="ایمیل",
        widget=forms.TextInput(
            attrs={
                'class': "peer inline-block w-full p-3 text-base outline dark:outline-none outline-1 -outline-offset-1 placeholder:text-transparent sm:text-sm/6 transition-all text-gray-800 dark:text-gray-100 dark:bg-gray-900 bg-slate-100 border border-transparent hover:border-slate-200 appearance-none rounded-md outline-none focus:bg-white focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 dark:focus:ring-blue-400",
                'placeholder': " ",
                'type': 'email'
            }
        )
    )