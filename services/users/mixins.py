from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

User = get_user_model()


class UserIsNotAuthenticatedMixin(UserPassesTestMixin):
    error_is_authenticated_message = None
    error_is_authenticated_redirect_viewname = None
    request = None

    def test_func(self):
        if self.request.user.is_authenticated:
            messages.info(self.request, self.error_is_authenticated_message)
            raise PermissionDenied
        return True

    def handle_no_permission(self):
        return redirect(self.error_is_authenticated_redirect_viewname)


class ValidationMessageMixin:

    def __init__(self):
        self.viewname = None
        self.message = None

    def make_confirmation_link(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        view_kwargs = dict(token=token, uidb64=uid)

        activation_url = reverse(self.viewname, kwargs=view_kwargs)
        current_site = Site.objects.get_current().domain

        return f"http://{current_site}{activation_url}"

    def get_message(self, user):
        activation_link = self.make_confirmation_link(user)
        return f"{self.message} {activation_link}"


class UserSaver:
    @staticmethod
    def get_user(uidb64):
        try:
            uid = urlsafe_base64_decode(uidb64)
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        return user

    @staticmethod
    def save_user_active(request, user):
        user.is_active = True
        user.save()
        login(request, user)

    @staticmethod
    def save_user_inactive(form):
        user = form.save(commit=False)
        user.is_active = False
        return user.save()
