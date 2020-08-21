from django.contrib.messages import get_messages
from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
import pytest


from .factories import UserProfileFactory, PostFactory
from .. import forms
from .. import models
from .. import views
from djangogram.views import HomePage


@pytest.mark.django_db
class TestHomeView():
    def test_anonymous(self, client):
        response = client.get('/')
        assert response.status_code == 302
        assert response.url == "/auth/login/"

    def test_home_page_user_is_not_member(self, client, user_created_by_manager):
        client.login(email='default_user@example.com',
                     password='default_user_password')
        response = client.get('/')
        assert response.status_code == 200

    def test_home_page_user_is_member(self, client, user_member_created_by_manager):
        client.login(email='default_user@example.com',
                     password='default_user_password')
        response = client.get('/')
        assert response.status_code == 200


class TestSignUpView():
    url = reverse('auth:signup')

    @pytest.mark.django_db
    def test_get_signup_view_user_is_not_authenticated(self, client, mailoutbox):
        response = client.get(self.url)
        assert response.status_code == 200

    @pytest.mark.django_db
    def test_sign_up_view_create_user(self, client, mailoutbox):
        data = {
            'name': 'user111',
            'email': 'email@example.com',
            'password1': 'gafea!MNe211',
            'password2': 'gafea!MNe211',
        }
        response = client.post(self.url, data)
        assert response.status_code == 302
        assert response.url == reverse('auth:login')
        assert models.UserProfile.objects.count() == 1
        assert len(mailoutbox) == 1
        mail = mailoutbox[0]
        assert mail.subject == 'Confirm you email address'
        assert mail.to[0] == models.UserProfile.objects.first().email
        uid = urlsafe_base64_encode(force_bytes(data['email']))
        assert uid in mail.body

    @pytest.mark.django_db
    def test_sign_up_view_create_user_no_email_input(self, client):
        response = client.post(self.url, {
            'name': 'user111',
            'email': '',
            'password1': 'gafea!MNe211',
            'password2': 'gafea!MNe211',
        })
        assert response.status_code == 200
        assert models.UserProfile.objects.all().count() == 0

    @pytest.mark.django_db
    def test_get_signup_view_user_is_authenticated(self,
                                                   client,
                                                   user_created_by_manager):
        client.login(email='default_user@example.com',
                     password='default_user_password')
        response = client.get(self.url)
        assert response.status_code == 302
        assert response.url == reverse('home')


class TestUserPostsView:

    @pytest.mark.django_db
    def test_user_posts_list_view(self, client, user_member_created_by_manager):
        posts = PostFactory.create_batch(
            3, user=user_member_created_by_manager)
        client.login(email='default_user@example.com',
                     password='default_user_password')
        response = client.get(
            f'/posts/by/{user_member_created_by_manager.id}/')
        assert response.status_code == 200
        assert len(response.context['object_list']) == 3
        assert response.context['post_user'] == user_member_created_by_manager
        assert response.context['is_users_page'] == True

    @pytest.mark.django_db
    def test_user_does_not_exist_posts_list_view_(self, client, user_member_created_by_manager):
        client.login(email='default_user@example.com',
                     password='default_user_password')

        response = client.get(
            f'/posts/by/{user_member_created_by_manager.id + 1}/')
        assert response.status_code == 404


class TestUserProfileWithPostsView:

    @pytest.mark.django_db
    def test_user_posts_list_view(self, client, user_member_created_by_manager):
        posts = PostFactory.create_batch(
            3, user=user_member_created_by_manager)
        client.login(email='default_user@example.com',
                     password='default_user_password')
        response = client.get(
            f'/auth/{user_member_created_by_manager.id}/')
        assert response.status_code == 200
        assert len(response.context['object_list']) == 3
        assert response.context['post_user'] == user_member_created_by_manager
        assert response.context['is_users_page'] == True

    @pytest.mark.django_db
    def test_user_does_not_exist_posts_list_view_(self, client, user_member_created_by_manager):
        client.login(email='default_user@example.com',
                     password='default_user_password')
        response = client.get(f'/auth/{user_member_created_by_manager.id+1}/')
        assert response.status_code == 404


class TestConfirmationEmailView:

    def test_confirmation_user_is_authenticated_and_not_member(self,
                                                               client,
                                                               user_created_by_manager,
                                                               member_group_fixture):
        email = user_created_by_manager.email
        client.login(email=email, password='default_user_password')
        uid = urlsafe_base64_encode(force_bytes(email))
        assert user_created_by_manager.groups.filter(
            name='Member').exists() == False
        response = client.get(f'/auth/activate/{uid}/')
        assert response.status_code == 200
        assert user_created_by_manager.groups.filter(
            name='Member').exists() == True
        assert response.content == b'Your email has been confirmed.'

    def test_confirmation_user_is_authenticated_and_member(self,
                                                           client,
                                                           user_member_created_by_manager):
        email = user_member_created_by_manager.email
        client.login(email=email, password='default_user_password')
        uid = urlsafe_base64_encode(force_bytes(email))
        response = client.get(f'/auth/activate/{uid}/')
        assert response.status_code == 302
        assert response.url == reverse('home')
        assert 'You email is already confirmed.' in response.cookies['messages'].value

    def test_confirmation_user_is_not_authenticated(self,
                                                    client,
                                                    user_member_created_by_manager):
        email = user_member_created_by_manager.email
        uid = urlsafe_base64_encode(force_bytes(email))
        response = client.get(f'/auth/activate/{uid}/')
        assert response.status_code == 200


