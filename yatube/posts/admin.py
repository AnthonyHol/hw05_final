from django.contrib import admin

from .models import Comment, Group, Post


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description',
    )
    list_editable = (
        'title',
        'slug',
        'description',
    )
    list_filter = ('title',)
    search_fields = ('title',)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'post',
        'pub_date',
        'author',
        'text',
    )
    list_editable = ('text',)
    search_fields = ('text',)
    list_filter = ('pub_date',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
