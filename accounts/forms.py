from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from allauth.account.forms import SignupForm, LoginForm
from django import forms
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email')


class CustomSignupForm(SignupForm):
    phone_number = forms.CharField(max_length=15, label='شماره تلفن', widget=forms.TextInput(attrs={'placeholder': '09123456789'}))

    def save(self, request):
        user = super().save(request)
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user

class CustomLoginForm(LoginForm):
    login = forms.CharField(label="ایمیل یا شماره تلفن", widget=forms.TextInput(attrs={'placeholder': 'Email or Phone Number'}))

    def __init__(self, *args, **kwargs):
        super(CustomLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].label = 'ایمیل یا شماره تلفن'
    def clean(self):
        login = self.cleaned_data.get('login')

        if login and login.isdigit():
            try:
                user = CustomUser.objects.get(phone_number=login)
                self.cleaned_data['login'] = user.email
            except CustomUser.DoesNotExist:
                raise forms.ValidationError("کاربری با این شماره تلفن یافت نشد.")
        return super().clean()