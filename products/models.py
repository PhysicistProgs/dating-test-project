import os

from django.db import models
from django.utils.deconstruct import deconstructible
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """
    Класс категории. Реализован с помощью mptt
    для удобства работы с деревом наследования
    """
    name = models.CharField(max_length=255, )
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    url = models.CharField(max_length=255, default='')

    def __str__(self):
        return self.name


@deconstructible
class UploadToImagesDir:
    """
    Класс необходим для передачи пути файла в upload_to
    """
    def __init__(self, sub_path):
        self.sub_path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f'{instance.name}.{ext}'
        return os.path.join(self.sub_path, filename)

upload_dir = UploadToImagesDir('product_photos/')


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    image = models.ImageField(upload_to=upload_dir, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
