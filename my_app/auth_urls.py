from django.contrib.auth import views as auth_views
from django.urls import re_path

from . import account_views

app_name = 'auth'

urlpatterns = [
    re_path(r'login/$', auth_views.LoginView.as_view(
        template_name='accounts/login.html'), name='login'),
    re_path(r'logout/$', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^signup/$', account_views.SignUpView.as_view(), name='signup'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
            account_views.ConfirmEmailView.as_view(), name='activate'),
    re_path(r'^(?P<pk>\d+)/$', account_views.UserProfileWithPostsView.as_view(), name='single'),
    re_path(r'^update_avatar/$', account_views.UpdateAvatarView.as_view(), name='update_avatar'),
]
