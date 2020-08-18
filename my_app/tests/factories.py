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

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        created_at = kwargs.pop('created_at', None)
        print(created_at)
        updated_at = kwargs.pop('updated_at', None)
        print(updated_at)
        obj = super(PostFactory, cls)._create(target_class, *args, **kwargs)
        if created_at is not None:
            obj.created_at = created_at
        if updated_at is not None:
            obj.updated_at = updated_at
        obj.save()
        return obj
  
    title = factory.Sequence(lambda n: f'post{n} title')
    message = factory.Sequence(lambda n: f'post{n} message')
    user = factory.SubFactory(UserProfileFactory)
    created_at = factory.Sequence(lambda n: datetime.datetime(2020,7,25,14,n,0,0))
    updated_at = factory.LazyAttribute(lambda o: o.created_at)
    

class ImageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Image

    user = factory.SubFactory(UserProfileFactory)
    post = factory.SubFactory(PostFactory)
    image = factory.django.ImageField()
    description = factory.LazyAttribute(lambda o: f'post{o.post.id} description')


class LikeDislikeFactory(factory.django.DjangoModelFactory):
    pass
