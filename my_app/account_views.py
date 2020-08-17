import cloudinary.uploader
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView, ListView, UpdateView

from .forms import SignUpForm, ConfirmRegistrationForm, UpdateAvatarForm
from .models import UserProfile


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
        group = Group.objects.get(name='ReadOnly')
        user.save()
        user.groups.add(group)
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


class UserProfileWithPostsView(ListView):
    template_name = 'accounts/profile.html'

    def get_queryset(self):
        try:
            self.post_user = UserProfile.objects.prefetch_related('posts').get(
                pk=self.kwargs.get('pk')
            )
            self.can_upload_avatar = self.post_user.id == self.request.user.id
        except UserProfile.DoesNotExist:
            raise Http404
        else:
            return self.post_user.posts.prefetch_related('images').order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = UserProfile.objects.get(
            pk=self.kwargs.get('pk'))
        context['post_user'] = self.post_user
        context['can_upload_avatar'] = self.can_upload_avatar
        return context


class ConfirmEmailView(LoginView):
    template_name = 'accounts/confirmation_login.html'
    authentication_form = ConfirmRegistrationForm

    def change_from_read_only_to_member(self, user):
        read_only_group = Group.objects.get(name='ReadOnly')
        read_only_group.user_set.remove(user)
        user.groups.add(Group.objects.get(name='Member'))
        user.save()

    def get(self, request, uidb64, *args, **kwargs):
        user = request.user
        user_groups = user.groups
        if user_groups.filter(name='Member').exists():
            messages.info(self.request, 'You email is alredy confirmed.')
            return redirect(reverse('home'))
        elif not user.is_authenticated:
            return self.render_to_response(self.get_context_data())
        elif user_groups.filter(name='ReadOnly').exists():
            self.change_from_read_only_to_member(user)
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
            self.change_from_read_only_to_member(user)
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
        cloudinary.uploader.destroy(UserProfile.objects.get(pk=self.object.id).
                                    avatar.public_id, invalidate=True)
        return super().form_valid(form)
