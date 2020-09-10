from django.shortcuts import HttpResponse
from django.shortcuts import render
from social_django.utils import load_strategy


def require_email(request):
    strategy = load_strategy()
    partial_token = request.GET.get('partial_token')
    partial = strategy.partial_load(partial_token)
    return render(
        request, 'social_auth/acquire_email.html', {
            'email_required': True,
            'partial_backend_name': partial.backend,
            'partial_token': partial_token
        }
    )


def validation_sent(request):
    """Email validation sent confirmation page"""
    email = request.session.get('email_validation_address')
    return HttpResponse(f'Confirmation link was sent to {email}')
