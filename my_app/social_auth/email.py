from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse


def send_validation(strategy, backend, code, partial_token):
    url = '{0}?verification_code={1}&partial_token={2}'.format(
        reverse('social:complete', args=(backend.name,)),
        code.code,
        partial_token
    )
    url = strategy.request.build_absolute_uri(url)
    send_mail('Validate your account', f'Validate your account {url}'.format(url),
              settings.DEFAULT_FROM_EMAIL, [code.email], fail_silently=False)
