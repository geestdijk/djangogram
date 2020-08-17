from cloudinary.forms import CloudinaryFileField
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _

from .models import Post, UserProfile


class SignUpForm(UserCreationForm):

    class Meta(UserCreationForm.Meta):
        model = UserProfile
        exclude = ('username',)
        fields = [
            'name',
            'email',
        ]


class PostForm(forms.ModelForm):
    message = forms.Textarea()

    class Meta:
        model = Post
        fields = ['title', 'message', ]


class PostImageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop('user_id', None)
        post_id = kwargs.pop('post_id', None)
        super().__init__(*args, **kwargs)
        self.fields['image'].options['folder'] = 'posts_images/user_{}/post_{}'.format(
            user_id, post_id)

    image = CloudinaryFileField(
        options={
            'crop': 'fill',
        },
    )

    class Meta:
        model = UserProfile
        fields = ['image', ]


class ConfirmRegistrationForm(AuthenticationForm):

    error_messages = {
        'invalid_login': _(
            "Please enter a correct password. Note that "
            "password is case-sensitive."
        ),
        'inactive': _("This account is inactive."),
    }

    def __init__(self, *args, **kwargs):
        self.email = kwargs.pop('email_from_link')
        super(ConfirmRegistrationForm, self).__init__(*args, **kwargs)
        self.fields.pop('username')

    def clean(self):
        username = self.email
        password = self.cleaned_data.get('password')
        if username is not None and password:
            self.user_cache = authenticate(
                self.request, username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data


class UpdateAvatarForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['avatar'].options['folder'] = 'avatar/user_{}'.format(
            kwargs['instance'].id)

    avatar = CloudinaryFileField(
        options={
            'crop': 'scale',
            'width': 200,
            'height': 200,
        },
    )

    class Meta:
        model = UserProfile
        fields = ['avatar', ]
