from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from homepage.forms import RegisterForm


class HomepageSecurityTests(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_form_weak_password_rejected(self):
        form_data = {
            'username': 'newuser',
            'user_mail': 'newuser@example.com',
            'password': '123',
            'password_confirm': '123'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)

    def test_logout_requires_post(self):
        url = reverse('homepage:logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

