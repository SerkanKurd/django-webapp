import email
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(
        required=True,
        label="Kullanıcı Adı"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Şifre"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Login', css_class='btn-primary'))


class RegisterForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        required=True,
        label="Kullanıcı Adı"
    )
    password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Şifre"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Şifre Tekrar"
    )

    user_mail = forms.EmailField(
        required=True,
        label="E-posta"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Kayıt Ol', css_class='btn-primary'))

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten alınmış.")
        return username

    def clean_user_mail(self):
        email = self.cleaned_data.get('user_mail')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresi zaten kullanılıyor.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        username = cleaned_data.get('username')

        if password and password_confirm:
            if password != password_confirm:
                self.add_error('password_confirm', "Şifreler eşleşmiyor.")
            else:
                user_obj = User(username=username) if username else None
                try:
                    validate_password(password, user=user_obj)
                except ValidationError as e:
                    self.add_error('password', e)
        return cleaned_data


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Adınız Soyadınız'}),
        label="Ad Soyad")
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'placeholder': 'E-posta'}),
        label="E-posta")
    message = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Mesajınız'}),
        label="Mesaj"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Gönder', css_class='btn-primary'))
