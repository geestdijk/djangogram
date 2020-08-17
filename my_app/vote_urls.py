from django.urls import re_path

from . import views
from .models import LikeDislike


app_name = 'vote'

urlpatterns = [
    re_path(r'^post/(?P<pk>\d+)/like/$',
        views.VotesView.as_view(vote_type=LikeDislike.LIKE),
        name='post_like'),
    re_path(r'^post/(?P<pk>\d+)/dislike/$',
        views.VotesView.as_view(vote_type=LikeDislike.DISLIKE),
        name='post_dislike'),
]
