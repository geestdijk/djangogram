import datetime
from unittest.mock import Mock

from django.contrib.auth.models import Group
import factory

from ..models import UserProfile, Post, Image, LikeDislike


class UserProfileFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = UserProfile
        django_get_or_create = ('email', 'name',)

    name = factory.Sequence(lambda n: f'test_user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.name}@example.com')

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

    title = factory.Sequence(lambda n: f'post{n} title')
    message = factory.Sequence(lambda n: f'post{n} message')
    created_at = datetime.datetime.now()
    updated_at = datetime.datetime.now()
    user = factory.SubFactory(UserProfileFactory)


class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Image

    user = factory.SubFactory(UserProfileFactory)
    post = factory.SubFactory(PostFactory)
    image = factory.django.ImageField()
    description = factory.LazyAttribute(lambda o: f'post{o.post.id} description')


class LikeDislikeFactory(factory.django.DjangoModelFactory):
    pass
