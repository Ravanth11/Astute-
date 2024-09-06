from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, UserManager
from django.utils import timezone

class User(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=150, unique=True)
    password = models.CharField(max_length=100)
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username


class BlogPost(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    content_md = models.TextField()
    content_html = models.TextField(blank=True, null=True)
    thumbnail = models.CharField(max_length=255, blank=True, null=True)
    author = models.CharField(max_length=50)
    date_created = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title


class Images(models.Model):
    id = models.AutoField(primary_key=True)
    image_data = models.BinaryField()
    image_name = models.CharField(max_length=255)
    url = models.URLField(max_length=255, unique=True)

    def __str__(self):
        return self.image_name
