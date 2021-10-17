import os
import random
from math import pi, sin, asin, sqrt, cos
from PIL import Image, ImageDraw, ImageFont
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext as _


class UserManager(BaseUserManager):
    """
    Почти полностью скопированный и переписанный UserManager из класса AbstractUser
    для реализации аутенификации через email.
    """
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


# Callable сущности для использования в модели User
def get_random_longitude():
    return round(random.uniform(54.803637, 55.199424), 6)

def get_random_latitude():
    return round(random.uniform(82.751897, 83.16019), 6)


@deconstructible
class UploadToAvatarDir:
    """
    Класс необходим для передачи пути файла в upload_to аттрибута avatar
    """
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f'{instance.email}.{ext}'
        return os.path.join(self.sub_path, filename)

upload_dir = UploadToAvatarDir('avatar/')


class User(AbstractBaseUser, PermissionsMixin):

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
    avatar = models.ImageField(upload_to=upload_dir)
    is_active = models.BooleanField(_('active'), default=True)

    # те, кого лайкнул пользователь
    liked_persons = models.ManyToManyField('self', symmetrical=False, blank=True)

    # случайная долгота и ширина в пределах Новосибирска
    longitude = models.FloatField(default=get_random_longitude, )
    latitude = models.FloatField(default=get_random_latitude, )

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

    def count_distance(self, user):
        """
        Расчет дистанции от self до user.
        """
        earth_radius = 6378.137
        if user.is_authenticated:
            # используем текущего вошедшего пользователя, если он есть
            lat1, long1 = user.latitude * pi / 180, user.longitude * pi / 180
        else:
            # иначе возьмем координаты центральной площади Новосибирска
            lat1, long1 = 82.920450 * pi / 180, 55.029997 * pi / 180
        lat2, long2 = self.latitude * pi / 180, self.longitude * pi / 180
        half_diff_latitudes = (lat1 - lat2) / 2
        half_diff_longitudes = (long1 - long2) / 2
        expr_under_sqrt = sin(half_diff_latitudes) ** 2 + cos(lat1) * cos(lat2) * sin(half_diff_longitudes) ** 2
        d = 2 * earth_radius * asin(sqrt(expr_under_sqrt))
        return round(d, 2)
