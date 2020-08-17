from django.urls import reverse, resolve


class TestUrls:
    def test_login_url(self):
        path = reverse('auth:login')
        assert resolve(path).view_name == ('auth:login')
