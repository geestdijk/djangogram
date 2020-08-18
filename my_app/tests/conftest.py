from django.contrib.auth.models import Group
import pytest
from pytest_factoryboy import register

from .factories import PostFactory
from ..models import UserProfile, Post


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
def superuser_created_by_manager(db):
    user = UserProfile.objects.create_superuser(name='Superuser',
                                                email='superuser@gmail.com',
                                                password='superuser_password')
    return user


register(PostFactory)
