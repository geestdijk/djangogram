import cloudinary.uploader
from cloudinary.models import CloudinaryField
from django.contrib.auth.models import (AbstractBaseUser,
                                        BaseUserManager,
                                        PermissionsMixin,
                                        Group)
from django.db import models
from django.db.models import Count, Q, Exists, OuterRef, Sum
from django.utils import timezone


class UserProfileManager(BaseUserManager):

    def create_user(self, email, name, password=None):
        if not email:
            raise ValueError('User must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password):
        user = self.create_user(email, name, password)
        user.is_superuser = True
        user.is_staff = True
        user.groups.add(Group.objects.get(name='Member'))
        user.save(using=self._db)
        return user


class UserProfile(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=155, unique=True)
    name = models.CharField(max_length=255)
    bio = models.TextField()
    avatar = CloudinaryField('avatar', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    follows = models.ManyToManyField(
        'UserProfile', related_name='followed_by', blank=True)

    def delete(self, using=None, keep_parents=False):
        cloudinary.uploader.destroy(self.avatar.public_id, invalidate=True)
        super().delete()

    objects = UserProfileManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', ]


class PostManager(models.Manager):

    def single_user_posts(self, post_user):
        return self.prefetch_related('images', 'votes').\
            annotate(votes_count_likes=Count('votes', filter=Q(votes__vote__gt=0)),
                     votes_count_dislikes=Count(
                'votes', filter=Q(votes__vote__lt=0)),
            liked_by_user=Exists(LikeDislike.objects.filter(
                user_id=post_user, post=OuterRef('pk'), vote=1)),
            disliked_by_user=Exists(LikeDislike.objects.filter(user_id=post_user, post=OuterRef('pk'), vote=-1)))

    def home_page_posts(self, user):
        return self.filter(user__in=[profile.id for profile in user.follows.all()]).\
            prefetch_related('images', 'votes', 'user').\
            annotate(votes_count_likes=Count('votes', filter=Q(votes__vote__gt=0)),
                     votes_count_dislikes=Count(
                'votes', filter=Q(votes__vote__lt=0)),
            liked_by_user=Exists(LikeDislike.objects.filter(
                user_id=user.id, post=OuterRef('pk'), vote=1)),
            disliked_by_user=Exists(LikeDislike.objects.filter(user_id=user.id,
                                                               post=OuterRef(
                                                                   'pk'),
                                                               vote=-1)))


class Post(models.Model):
    user = models.ForeignKey(
        UserProfile, related_name='posts', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'message']

    objects = PostManager()


class Image(models.Model):
    user = models.ForeignKey(
        UserProfile, related_name='images', on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, default=None, related_name='images', on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    image = CloudinaryField('image', null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def delete(self, using=None, keep_parents=False):
        cloudinary.uploader.destroy(self.image.public_id, invalidate=True)
        super().delete()


class LikeDislikeManager(models.Manager):
    use_for_related_fields = True

    def likes(self):
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        return self.get_queryset().filter(vote__lt=0)

    def sum_rating(self):
        return self.get_queryset().aggregate(Sum('vote')).get('vote__sum') or 0


class LikeDislike(models.Model):
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )

    vote = models.SmallIntegerField(verbose_name="Vote", choices=VOTES)
    user = models.ForeignKey(
        UserProfile, verbose_name="User", on_delete=models.CASCADE)
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='votes')

    def __str__(self):
        return f'{self.user}:post{self.post.id}:{self.vote}'

    class Meta:
        unique_together = ("user", "post", "vote")

    objects = LikeDislikeManager()
