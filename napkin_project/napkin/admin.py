from django.contrib import admin
from napkin.models import Group, Post

admin.site.register(Group)
admin.site.register(Post)
class GroupAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'name_slug', 'created')

class PostAdmin (admin.ModelAdmin):

