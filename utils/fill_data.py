import django
import os
import random
import sys

current_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_dir + '/..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangogram.settings')
django.setup()

import cloudinary.uploader
from django.contrib.auth.models import Group
from faker import Faker

from my_app.models import (UserProfile,
                           Post,
                           Image,
                           LikeDislike)


fake = Faker()
avatar_source = 'https://picsum.photos/200'
post_image_source = 'https://picsum.photos/1024/576'
NUM_OF_USERS = 50


# Creating UserProfiles
def create_users():
    member_group = Group.objects.get(name='Member')
    for i in range(NUM_OF_USERS):
        fake_name = f'user{i+1}'
        fake_email = f'{fake_name}@example.com'
        password = f'{fake_name}_password'
        new_user = UserProfile.objects.create_user(fake_email, fake_name, password=password)
        new_user.groups.add(member_group)
        new_user.bio = fake.text()
        folder = f'avatar/{new_user.id}'
        new_user.avatar =\
            cloudinary.uploader.upload_resource(
                avatar_source,
                folder=folder
            )
        new_user.save()


def create_posts():
    for user in UserProfile.objects.all():
        # creating 5-8 posts for each user
        for post_num in range(random.randint(5, 8)):
            new_post = Post.objects.create(
                user=user, title=fake.sentence(), message=fake.text())
            # adding 1-5 images to each post
            for image_num in range(random.randint(1, 5)):
                folder = f'posts_images/user_{user.id}/post_{new_post.id}'
                Image.objects.create(user=user, post=new_post,
                                     image=cloudinary.uploader.upload_resource(
                                         post_image_source,
                                         folder=folder
                                     ))


def add_follows():
    all_user_ids = [
        _ for _ in UserProfile.objects.values_list('id', flat=True)]
    for user in UserProfile.objects.all():
        # adding 5-15 follows
        for follow in random.sample(all_user_ids, random.randint(5, 15)):
            user.follows.add(UserProfile.objects.get(pk=follow))


def add_votes():
    all_posts_ids = [_ for _ in Post.objects.values_list('id', flat=True)]
    for user in UserProfile.objects.all():
        # each user votes from  to 200 times
        for post_id in random.sample(all_posts_ids, random.randint(100, 200)):
            LikeDislike.objects.create(
                vote=random.choice((-1, 1)),
                user=user,
                post=Post.objects.get(pk=post_id)
            )


if __name__ == "__main__":
    create_users()
    create_posts()
    add_follows()
    add_votes()
