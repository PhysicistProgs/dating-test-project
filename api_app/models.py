import os
from uuid import uuid4
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import ugettext as _


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    @staticmethod
    def path_and_rename(path):
        """
        Возвращает функцию, которая в момент вызова изменит
        имя файла, оставив расширение тем же. Имя файла случайное на основе uuid.
        Используется для аргумента upload_to поля avatar.
        """
        def wrapper(instance, filename):
            ext = filename.split('.')[-1]
            filename = f'avatar{str(uuid4())[:8]}.{ext}'
            return os.path.join(path, filename)

        return wrapper

    MALE = 'M'
    FEMALE = 'F'
    SEX_CHOICES = (
        (MALE, 'Male'),
        (FEMALE, 'Female')
    )
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=30)
    last_name = models.CharField(_('last name'), max_length=30)
    sex = models.CharField(_('sex'), choices=SEX_CHOICES, max_length=30)
    avatar = models.ImageField(upload_to=path_and_rename.__func__('avatar'))
    is_active = models.BooleanField(_('active'), default=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    objects = UserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def watermark_image(self, image_path):
        """
        Меняет фотографию по адресу image_path.
        На данный момент добавляет надпись WaterMark,
        но можно реализовать любую логику.
        """
        im = Image.open(image_path)
        width, height = im.size
        draw = ImageDraw.Draw(im)
        font = ImageFont.load_default()
        draw.text((width/2, height/2), "WaterMark",
                  (0, 0, 0), font=font)
        im.save(image_path, 'JPEG')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        path = self.avatar.path
        self.watermark_image(path)

