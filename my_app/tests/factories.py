import datetime
import pytz
from unittest.mock import Mock

from django.contrib.auth.models import Group
import factory

from ..models import UserProfile, Post, Image, LikeDislike

utc_timezone = pytz.timezone('UTC')


class UserProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = UserProfile
        django_get_or_create = ('email', 'name')

    id = factory.Sequence(lambda n: int(n))
    name = factory.Sequence(lambda n: f'test_user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.name}@example.com')
    is_active = True

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for group in extracted:
                self.groups.add(group)


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Post

    id = factory.Sequence(lambda n: int(n))
    title = factory.Sequence(lambda n: f'post{n} title')
    message = factory.Sequence(lambda n: f'post{n} message')
    user = factory.SubFactory(UserProfileFactory)
    created_at = factory.Sequence(lambda n: datetime.datetime(2020, 7, 25,
                                                              hour=14, minute=n, 
                                                              second=0, microsecond=0, 
                                                              tzinfo=utc_timezone))
    updated_at = factory.LazyAttribute(lambda o: o.created_at)


class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Image

    user = factory.SubFactory(UserProfileFactory)
    post = factory.SubFactory(PostFactory)
    image = factory.django.ImageField()
    description = factory.Sequence(lambda n: f'image{n} description')


class LikeDislikeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = LikeDislike
        django_get_or_create = ('vote', 'user', 'post')

    user = factory.SubFactory(UserProfileFactory)
    post = factory.SubFactory(PostFactory)
    vote = 1
