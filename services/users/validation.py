from django.conf import settings
from django.core.mail import send_mail
from mixins import ValidationMessageMixin, UserSaver


class BaseValidator(ValidationMessageMixin, UserSaver):
    subject_registration = None
    subject_reset = None
    message_registration = None
    message_reset = None
    viewname_registration = None
    viewname_reset = None

    def __init__(self, registration, **kwargs):
        super().__init__()
        self.registration = registration
        self.subject = None
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


class EmailValidator(BaseValidator):
    subject_registration = 'Подтвердите адрес электронной почты'
    subject_reset = 'Подтвердите смену пароля'
    message_registration = 'Для окончания регистрации необходимо подтвердить вашу электронную почту.\
            Чтобы это сделать, перейдите по ссылке:'
    message_reset = "Чтобы сбросить пароль, необходимо пройти по ссылке:"
    viewname_registration = "users:register_mail_activation"
    viewname_reset = "users:reset_mail_activation"

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
