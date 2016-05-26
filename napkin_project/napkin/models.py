from __future__ import unicode_literals
from django.template.defaultfilters import slugify
from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=24, unique=True, blank=False)
    name_slug = models.SlugField(blank=True)
    created = models.DateTimeField(auto_now_add=True, blank=True)

    def save(self, *args, **kwargs):
        self.name_slug = slugify(self.name)
        super(Group, self).save(*args, **kwargs)


class Post(models.Model):
    group = models.ForeignKey(Group)
    url = models.URLField(blank=True)
    text = models.CharField(max_length=1000,blank=False)
    created = models.DateTimeField(auto_now_add=True)
