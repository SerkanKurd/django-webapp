from django.test import TestCase
from paragliding.forms import PilotForm


class ParaglidingSecurityTests(TestCase):

    def test_pilot_form_ssrf_urls_rejected(self):
        malicious_urls = [
            "http://169.254.169.254/latest/meta-data/",
            "http://localhost:8000/internal",
            "https://evil.com/leonardo/pilot/0_1234",
            "file:///etc/passwd",
        ]
        for url in malicious_urls:
            form = PilotForm(data={
                'name': 'Test Pilot',
                'profile_url': url,
                'level': 'P3'
            })
            self.assertFalse(form.is_valid(), f"URL should be rejected: {url}")
            self.assertIn('profile_url', form.errors)

