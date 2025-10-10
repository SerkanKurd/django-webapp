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

