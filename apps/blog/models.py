from django.db import models
from django.conf import settings

from apps.blog.constants import (
    CATEGORY_NAME_MAX_LENGTH,
    POST_STATUS_MAX_LENGTH,
    POST_TITLE_MAX_LENGTH,
    STATUS_DRAFT,
    STATUS_PUBLISHED,
    TAG_NAME_LENGTH,
)

class Category(models.Model):
    name = models.CharField(max_length=CATEGORY_NAME_MAX_LENGTH, unique=True)
    slug = models.SlugField(unique=True)

class Tag(models.Model):
    name= models.CharField(max_length=TAG_NAME_LENGTH, unique=True)
    slug = models.SlugField(unique=True)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = STATUS_DRAFT, 'Draft'
        PUBLISHED = STATUS_PUBLISHED, 'Published'

    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=POST_TITLE_MAX_LENGTH)
    slug = models.SlugField(unique=True)
    body = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField(Tag, blank=True)
    status = models.CharField(
        max_length=POST_STATUS_MAX_LENGTH,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)