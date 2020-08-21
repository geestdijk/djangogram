import cloudinary.uploader
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.forms import modelformset_factory
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views import generic
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView, ListView, UpdateView

from .forms import (PostForm,
                    PostImageForm,
                    SignUpForm,
                    ConfirmRegistrationForm,
                    UpdateAvatarForm)
from .models import UserProfile, Post, Image, LikeDislike


class SignUpView(CreateView):
    def get(self, request, *args, **kwargs):
        context = {'form': SignUpForm()}
        return render(request, 'accounts/signup.html', context)

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if not form.is_valid():
            form = SignUpForm()
            return render(request, 'accounts/signup.html', {'form': form})
        user = form.save(commit=False)
        user.save()
        current_site = get_current_site(request)
        email_subject = 'Confirm you email address'
        message = render_to_string('accounts/activate_account.html', {
            'user': user,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(user.email)),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(email_subject, message, to=[to_email])
        email.send()
        messages.info(self.request,
                      '''We have sent you an email,
please confirm your email address to complete registration'''
                      )
        return redirect(reverse('auth:login'))


class UserPostsMixin():

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.is_users_page = self.post_user.id == self.request.user.id
        context['post_user'] = self.post_user
        context['is_users_page'] = self.is_users_page
        return context


class UserProfileWithPostsView(UserPostsMixin, ListView):
    template_name = 'accounts/profile.html'

    def get_queryset(self):
        try:
            self.post_user = UserProfile.objects.prefetch_related('posts').get(
                pk=self.kwargs.get('pk')
            )
        except UserProfile.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.prefetch_related('images').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = UserProfile.objects.get(
            pk=self.kwargs.get('pk'))
        return context


class ConfirmEmailView(LoginView):
    template_name = 'accounts/confirmation_login.html'
    authentication_form = ConfirmRegistrationForm

    def get(self, request, uidb64, *args, **kwargs):
        user = request.user
        user_groups = user.groups
        if user_groups.filter(name='Member').exists():
            messages.info(self.request, 'You email is already confirmed.')
            return redirect(reverse('home'))
        elif not user.is_authenticated:
            return self.render_to_response(self.get_context_data())
        elif not user_groups.filter(name='Member').exists():
            user.groups.add(Group.objects.get(name='Member'))
            return HttpResponse('Your email has been confirmed.')

    def get_form_kwargs(self):
        self.email_from_link = force_text(
            urlsafe_base64_decode(self.kwargs['uidb64']))
        kwargs = super(ConfirmEmailView, self).get_form_kwargs()
        kwargs.update({'email_from_link': self.email_from_link})
        return kwargs

    def post(self, request, uidb64, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            user = UserProfile.objects.get(email=form.email)
            if 'Member' in user.groups.values_list('name', flat=True):
                return HttpResponse('You email is already confirmed.')
            user.groups.add(Group.objects.get(name='Member'))
            return self.form_valid(form)
        return self.form_invalid(form)


class UpdateAvatarView(UpdateView):
    model = UserProfile
    form_class = UpdateAvatarForm
    template_name = 'accounts/update_avatar.html'

    def get_success_url(self):
        return reverse('auth:single', kwargs={'pk': self.object.id})

    def get_object(self):
        return UserProfile.objects.get(pk=self.request.user.id)

    def form_valid(self, form):
        user = UserProfile.objects.get(pk=self.object.id)
        if user.avatar:
            cloudinary.uploader.destroy(user.avatar.public_id, invalidate=True)
        return super().form_valid(form)


class UserPosts(UserPostsMixin, generic.ListView):
    template_name = 'posts/user_post_list.html'

    def get_queryset(self):
        try:
            self.post_user = UserProfile.objects.prefetch_related('posts').get(
                pk=self.kwargs.get('user_pk')
            )
            self.is_users_page = self.request.user.id == self.post_user.id
        except UserProfile.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.single_user_posts(self.post_user)
            

class HomePageFeedView(generic.ListView):
    template_name = 'index.html'

    def get_queryset(self):
        return Post.objects.home_page_posts(self.request.user)


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'posts/post_detail.html'


def create_post(request):
    ImageFormSet = modelformset_factory(Image, form=PostImageForm, extra=4)
    if request.method == 'POST':
        postForm = PostForm(request.POST)
        if postForm.is_valid():
            post_form = postForm.save(commit=False)
            post_form.user = request.user
            post_form.save()
            formset = ImageFormSet(request.POST, request.FILES,
                                   queryset=Image.objects.none(), form_kwargs={
                                       'user_id': request.user.id,
                                       'post_id': post_form.id
                                   })
            if formset.is_valid():
                for form in formset.cleaned_data:
                    if not form:
                        continue
                    user = request.user
                    image = form['image']
                    pic = Image(post=post_form, image=image, user=user)
                    pic.save()
                return HttpResponseRedirect(
                    reverse('posts:for_user', kwargs={'user_pk': request.user.pk}))
            else:
                post_form.delete()
    postForm = PostForm()
    formset = ImageFormSet(queryset=Image.objects.none())
    return render(request, 'posts/create_post.html',
                  {'postForm': postForm, 'formset': formset})


class VotesView(generic.View):
    vote_type = None

    def post(self, request, pk):
        obj = Post.objects.get(id=pk)
        try:
            likedislike = LikeDislike.objects.get(post=obj, user=request.user)
            if likedislike.vote is not self.vote_type:
                likedislike.vote = self.vote_type
                likedislike.save(update_fields=['vote'])
            else:
                likedislike.delete()
        except LikeDislike.DoesNotExist:
            obj.votes.create(user=request.user, vote=self.vote_type)

        return redirect(request.META['HTTP_REFERER'])
