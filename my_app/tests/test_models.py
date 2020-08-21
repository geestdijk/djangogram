import datetime
from unittest import mock

import pytest

from .. import models
from .factories import (utc_timezone,
                        ImageFactory,
                        UserProfileFactory,
                        PostFactory,
                        LikeDislikeFactory)


pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures("reset_factory_sequences")
class TestModels:

    def test_user_profile(self):
        UserProfileFactory.create()
        assert models.UserProfile.objects.count() == 1

    def test_user_manager(self, user_created_by_manager):
        assert user_created_by_manager.name == 'Default User'
        assert user_created_by_manager.email == 'default_user@example.com'
        assert user_created_by_manager.check_password('default_user_password')
        assert user_created_by_manager.is_active == True
        assert user_created_by_manager.is_superuser == False
        assert user_created_by_manager.is_staff == False
        assert models.UserProfile.objects.count() == 1


    def test_create_user_without_email(self):
        with pytest.raises(ValueError):
            models.UserProfile.objects.create_user(name='some_user', email=None)


    def test_superuser_manager(self, member_group_fixture, superuser_created_by_manager):
        assert superuser_created_by_manager.is_superuser == True
        assert superuser_created_by_manager.is_staff == True
        assert superuser_created_by_manager.groups.first().name == 'Member'


    @pytest.mark.parametrize(
        'date_created',
        [datetime.datetime(2020, 7, 25,
                        hour=14, minute=1,
                        second=0, microsecond=0,
                        tzinfo=utc_timezone)]
    )
    @pytest.mark.freeze_time('2020-07-27 14:02:00', tz_offset=0)
    def test_post(self, date_created):
        post = PostFactory.build()

        assert post.title == 'post1 title'
        assert post.message == 'post1 message'
        assert post.created_at == date_created
        assert post.updated_at == date_created


    def test_create_image(self):
        my_image = ImageFactory.build()
        assert my_image.user.email == 'test_user1@example.com'
        assert my_image.post.title == 'post1 title'
        assert my_image.image.name == 'example.jpg'
        assert my_image.description == 'image1 description'


    def test_likedislike(self):
        PostFactory.reset_sequence(1)
        UserProfileFactory.reset_sequence(1)
        likedislike = LikeDislikeFactory.create()
        assert models.LikeDislike.objects.all().count() == 1
        assert str(likedislike) == 'test_user1@example.com:post1:1'
        

    def test_likedislike_manager(self):
        post = PostFactory.create()
        for i in [1, -1, 1, 1, -1]:
            LikeDislikeFactory.create(post=post, vote=i)
        assert models.LikeDislike.objects.all().count() == 5
        assert post.votes.likes().count() == 3
        assert post.votes.dislikes().count() == 2
        assert post.votes.sum_rating() == 1
            
