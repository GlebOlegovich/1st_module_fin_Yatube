from django.contrib import admin

from .models import Comment, Follow, Group, Post


class PostAdmin(admin.ModelAdmin):
    '''
    Админка постов:\n
    в ней доступны pk, text, дата публикации,\n
    автор, название группы (от которой сделана публикация)\n
    Есть:
    1) Сортировка по дате публикации\n
    2) Возможность изменить из админки группу, которая сделала пост
    (Админы могут зарабатывать на плагиате :-0,
    переприсваивать записи другим группам)\n
    3) Поиск по text публикации\n
    4) Если в поле ничего не вбито - будет дефолтное значение: -пусто-
    '''
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


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)
