from typing import Any

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

from apps.auths.constants import (
    EMAIL_FIELD,
    FIRST_NAME_FIELD,
    FIRST_NAME_MAX_LENGTH,
    IS_STAFF_FIELD,
    IS_SUPERUSER_FIELD,
    LAST_NAME_FIELD,
    LAST_NAME_MAX_LENGTH,
)


class UserManager(BaseUserManager):
    def create_user(self, email:str, password: str | None = None, **extra_fields: Any) -> 'User':
        user = self.model(email=self.normalize_email(email).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self,
            email: str,
            password: str | None = None,
            **extra_fields: Any
            ) -> 'User':
        extra_fields.setdefault(IS_STAFF_FIELD, True)
        extra_fields.setdefault(IS_SUPERUSER_FIELD, True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=FIRST_NAME_MAX_LENGTH)
    last_name = models.CharField(max_length=LAST_NAME_MAX_LENGTH)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = EMAIL_FIELD
    REQUIRED_FIELDS = [FIRST_NAME_FIELD, LAST_NAME_FIELD]
