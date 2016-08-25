from django.contrib import admin
from napkin.models import Group, Post, Subscriber

class GroupAdmin (admin.ModelAdmin):
    list_display = ('id', 'name', 'name_slug', 'created', 'subscribed_users')
    ordering = ('-created',)

    def subscribed_users(self, obj):
        return obj.subscribers.count()


class PostAdmin (admin.ModelAdmin):
    list_display = ('id', 'group_name', 'url', 'text', 'created', 'hits',)

    def group_name(self, obj):
        return obj.group.name
    group_name.short_description = 'Group Name'
    group_name.admin_order_field = 'group'


class SubscriberAdmin (admin.ModelAdmin):
    list_display = ('email', 'created',)


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Subscriber, SubscriberAdmin)
