from django.contrib import admin
from napkin.models import Group, Post

class GroupAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'name_slug', 'created')

class PostAdmin (admin.ModelAdmin):
    list_display = ('id', 'group_name', 'url', 'text', 'created')

    def group_name(self, obj):
        return obj.group.name
    group_name.short_description = 'Group Name'
    group_name.admin_order_field = 'group'

admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
