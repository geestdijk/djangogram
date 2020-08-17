import re

from django.conf import settings
from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse


EXEMPT_URLS = [re.compile(settings.LOGIN_URL.lstrip('/'))]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
    EXEMPT_URLS += [re.compile(url) for url in settings.LOGIN_EXEMPT_URLS]
if hasattr(settings, 'MEMBER_EXEMPT_URLS'):
    MEMBER_EXEMPT_URLS = [re.compile(url)
                          for url in settings.MEMBER_EXEMPT_URLS]


class MembershipRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request, 'user')
        path = request.path_info.lstrip('/')
        url_is_login_exempt = any(url.match(path) for url in EXEMPT_URLS)
        url_is_member_exempt = any(url.match(path)
                                   for url in MEMBER_EXEMPT_URLS)
        current_user_is_member = request.user.groups.filter(
            name='Member').exists()

        if path == reverse('auth:logout').lstrip('/'):
            logout(request)

        if url_is_login_exempt and request.user.is_authenticated:
            return redirect(settings.LOGIN_REDIRECT_URL)
        elif request.user.is_authenticated and url_is_member_exempt\
                and not current_user_is_member:
            return HttpResponse('Please confirm your email')
        elif current_user_is_member or url_is_login_exempt or request.user.is_authenticated:
            return
        else:
            return redirect(settings.LOGIN_URL)
