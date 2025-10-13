from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class LoginForm(forms.Form):  # Or inherit from Django's AuthenticationForm
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(
            Submit('submit', 'Login', css_class='btn-primary'))


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

