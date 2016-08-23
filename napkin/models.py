from __future__ import unicode_literals
from django.template.defaultfilters import slugify
from django.db import models


class Subscriber(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    email = models.EmailField()


class Group(models.Model):
    name = models.CharField(max_length=24, unique=True, blank=False)
    name_slug = models.SlugField(blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    subscribers = models.ManyToManyField(to=Subscriber)

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)


class Post(models.Model):
    group = models.ForeignKey(Group)
    url = models.URLField(blank=True)
    title = models.CharField(max_length=600, blank=True)
    site_name = models.CharField(max_length=600, blank=True)
    site_url = models.CharField(max_length=600, blank=True)
    text = models.CharField(max_length=1000,blank=False)
    created = models.DateTimeField(auto_now_add=True)
    hits = models.IntegerField(blank=True, default=0)

    def save(self, *args, **kwargs):
        if not self.hits:
            self.hits = 0
        return super(Post, self).save(*args, **kwargs)
