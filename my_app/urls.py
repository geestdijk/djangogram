from django.contrib.auth import views as auth_views
from django.urls import include, path, re_path

from . import views
from .models import LikeDislike


auth_patterns = ([
    re_path(r'login/$', auth_views.LoginView.as_view(
        template_name='accounts/login.html'), name='login'),
    re_path(r'logout/$', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^signup/$', views.SignUpView.as_view(), name='signup'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/$',
            views.ConfirmEmailView.as_view(), name='activate'),
    re_path(r'^(?P<pk>\d+)/$',
            views.UserProfileWithPostsView.as_view(), name='single'),
    re_path(r'^update_avatar/$', views.UpdateAvatarView.as_view(),
            name='update_avatar'),
], 'auth')


post_patterns = ([
    re_path(r'^new/$', views.create_post, name='create'),
    re_path(r'^by/(?P<user_pk>\d+)/$',
            views.UserPosts.as_view(), name='for_user'),
    re_path(r'^(?P<pk>\d+)/$', views.PostDetail.as_view(), name='single_post'),
], 'posts')


vote_patterns = ([
    re_path(r'^post/(?P<pk>\d+)/like/$',
            views.VotesView.as_view(vote_type=LikeDislike.LIKE),
            name='post_like'),
    re_path(r'^post/(?P<pk>\d+)/dislike/$',
            views.VotesView.as_view(vote_type=LikeDislike.DISLIKE),
            name='post_dislike'),
], 'vote')

urlpatterns = [
    path('posts/', include(post_patterns)),
    path('auth/', include(auth_patterns)),
    path('api/', include(vote_patterns)),
]
