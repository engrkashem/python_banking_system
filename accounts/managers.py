# from django.db import models
# from django.contrib import auth
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **args):
        if not email:
            raise ValueError('Email is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **args)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email=None, password=None, **args):
        args.setdefault('is_staff', False)
        args.setdefault('is_superuser', False)
        return self._create_user(email, password, **args)

    def create_superuser(self, email, password, **args):
        args.setdefault('is_staff', True)
        args.setdefault('is_superuser', True)
        if args.get('is_staff') is not True:
            raise ValueError("You must have a staff access")
        if args.get('is_superuser') is not True:
            raise ValueError("You must have a superuser access")
        return self._create_user(self, email, password=None, **args)
