import datetime
from unittest import mock

import pytest

from .. import models


pytestmark = pytest.mark.django_db


def test_user_manager(user_created_by_manager):
    assert user_created_by_manager.name == 'Default User'
    assert user_created_by_manager.email == 'default_user@example.com'
    assert user_created_by_manager.check_password('default_user_password')
    assert user_created_by_manager.is_active == True
    assert user_created_by_manager.is_superuser == False
    assert user_created_by_manager.is_staff == False


def test_superuser_manager(member_group_fixture, superuser_created_by_manager):
    assert superuser_created_by_manager.is_superuser == True
    assert superuser_created_by_manager.is_staff == True
    assert superuser_created_by_manager.groups.first().name == 'Member'


def test_post(mocker, post_factory):
    datetime_mock = mocker.patch("my_app.models.datetime",)
    datetime_mock.datetime.now.return_value=datetime.datetime(2020,7,27,14,2,0,0)
    post = post_factory()
    
    assert post.title == 'post0 title'
    assert post.message == 'post0 message'
    assert isinstance(post.user, models.UserProfile)
    assert post.created_at == datetime.datetime(2020,7,25,14,0,0,0)
    assert post.updated_at == datetime.datetime(2020,7,25,14,0,0,0)
