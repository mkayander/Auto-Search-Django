from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.html import format_html, format_html_join
from django.utils.translation import ugettext as _

from account.models import Account
from .models import Profile


def make_html_list(help_texts):
    help_items = format_html_join('', '<li>{}</li>', ((help_text,) for help_text in help_texts))
    return format_html('<ul>{}</ul>', help_items) if help_items else ''


class UserRegisterForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "Пароли не совпадают",
        'invalid': "Пользователь с таким e-mail уже существует",
    }

    email = forms.EmailField()
    email.label = _('E-mail')
    email.help_text = _('Please enter your E-mail.')

    # def clean_email(self):
    #     email = self.cleaned_data["email"]
    #     if email and Account.objects.filter(email=email).exists():
    #         raise forms.ValidationError(
    #             self.error_messages['invalid'],
    #             code='invalid',
    #             )
    #     return email

    class Meta:
        model = Account
        fields = ['username', 'email', 'password1', 'password2']


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    email.label = _('E-mail')
    email.help_text = _('Enter your new E-mail here.')

    class Meta:
        model = Account
        fields = ['username', 'email']


class ProfileUpdateForm(forms.ModelForm):
    # bio = forms.TextInput()
    class Meta:
        model = Profile
        fields = ['image']
