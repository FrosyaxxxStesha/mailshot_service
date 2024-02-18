from django.contrib.sites.models import Site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.contrib.auth import get_user_model, login
from django.conf import settings
from django.core.mail import send_mail


User = get_user_model()


class EmailValidator:
    subject_registration = 'Подтвердите адрес электронной почты'
    subject_reset = 'Подтвердите смену пароля'
    message_registration = 'Для окончания регистрации необходимо подтвердить вашу электронную почту.\
            Чтобы это сделать, перейдите по ссылке:'
    message_reset = "Чтобы сбросить пароль, необходимо пройти по ссылке:"
    viewname_registration = "users:register_mail_activation"
    viewname_reset = "users:reset_mail_activation"

    def __init__(self, registration, **kwargs):
        self.registration = registration
        self.message = None
        self.subject = None
        self.viewname = None
        self.from_email = None

        for k, v in kwargs.items():
            setattr(self, k, v)

        self.setup()

    def setup(self):
        if self.registration:
            self.registration_setup()
        else:
            self.reset_setup()

    def registration_setup(self):
        self.message = self.message_registration
        self.subject = self.message_registration
        self.viewname = self.viewname_registration

    def reset_setup(self):
        self.message = self.message_reset
        self.subject = self.message_reset
        self.viewname = self.viewname_reset

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

    @staticmethod
    def save_user_inactive(form):
        user = form.save(commit=False)
        user.is_active = False
        return user.save()

    def send_validation_mail(self, form):
        user = self.save_user_inactive(form)
        kwargs = dict(
            subject=self.subject,
            message=self.get_message(user),
            from_email=self.from_email if self.from_email is not None else settings.EMAIL_HOST_USER,
            reciplient_list=[user.email],
            fail_silently=False
        )
        response = send_mail(**kwargs)

        return bool(response)
