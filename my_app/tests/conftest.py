from django.contrib.auth.models import Group
import pytest
from pytest_factoryboy import register

from . import factories
from ..models import UserProfile, Post


@pytest.fixture(autouse=True, scope='function')
def reset_factory_sequences():
    factories.UserProfileFactory.reset_sequence(1)
    factories.PostFactory.reset_sequence(1)
    factories.ImageFactory.reset_sequence(1)
    factories.LikeDislikeFactory.reset_sequence()


@pytest.fixture
def member_group_fixture(db):
    member_group, _ = Group.objects.get_or_create(name='Member')
    return member_group


@pytest.fixture
def user_created_by_manager(db):
    user = UserProfile.objects.create_user(name='Default User',
                                           email='default_user@example.com',
                                           password='default_user_password')
    return user


@pytest.fixture
def user_member_created_by_manager(db, member_group_fixture):
    user = UserProfile.objects.create_user(name='Default User',
                                           email='default_user@example.com',
                                           password='default_user_password')
    user.groups.add(member_group_fixture)
    return user


@pytest.fixture
def superuser_created_by_manager(db):
    user = UserProfile.objects.create_superuser(name='Superuser',
                                                email='superuser@gmail.com',
                                                password='superuser_password')
    return user
