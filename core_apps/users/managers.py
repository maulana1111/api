from django.apps import apps
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
# Create your tests here.

def validate_email_address(email: str):
    try:
        validate_email(email)
    except ValidationError:
        raise ValidationError(_("Enter a valid email address"))

class UserManager(DjangoUserManager):
    def _create_user(
        self, 
        username: str, 
        email: str, 
        password: str | None, 
        **extra_field
    ):
        if not username:
            raise ValidationError(_("An Username must be provided"))
        if not email:
            raise ValidationError(_("An Email address must be provided"))

        email = self.normalize_email(email)
        validate_email_address(email)
        global_user_model = apps.get_model(
            self.model._meta.app_lebel, self.model._meta.object_name
        )
        username = global_user_model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_field)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self, 
        username: str, 
        email: str | None =None, 
        password: str | None =None, 
        **extra_field
    ):
        extra_field.setdefault("is_staff", False)
        extra_field.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_field)

    def create_superuser(
        self, 
        username: str, 
        email: str | None =None, 
        password: str | None =None, 
        **extra_field
    ):
        extra_field.setdefault("is_staff", True)
        extra_field.setdefault("is_superuser", True)
        if extra_field.get("is_staff") is not True:
            raise ValidationError(_("Superuser must have is_staff=True."))
        if extra_field.get("is_superuser") is not True:
            raise ValidationError(_("Superuser must have is_superuser=True."))

        return self._create_user(username, email, password, **extra_field)

