from django.contrib import admin

from posts.models import (Group, Post, Comment, Follow)


class PostAdmin(admin.ModelAdmin):
    """ Класс для работы в админ-панели."""
    # Список полей, которые отображаются в админке
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    # Список редактируемых полей
    list_editable = ('group',)
    # Поля которые поддерживают поиск
    search_fields = ('text',)
    # Поля, которые поддерживают фильтр
    list_filter = ('pub_date',)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """ Класс для работы в админ-панели."""
    # Список полей, которые отображаются в админке
    list_display = ('pk', 'title', 'slug', 'description')
    # Список редактируемых полей
    list_editable = ('title', 'description')
    # Поля которые поддерживают поиск
    search_fields = ('title',)
    # Поля, которые поддерживают фильтр
    list_filter = ('title',)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    """ Класс для работы в админ-панели."""
    # Список полей, которые отображаются в админке
    list_display = ('pk', 'text', 'created', 'author',)
    # Список редактируемых полей
    list_editable = ('text', )
    # Поля которые поддерживают поиск
    search_fields = ('text',)
    # Поля, которые поддерживают фильтр
    list_filter = ('author',)
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """ Класс для работы в админ-панели."""
    # Список полей, которые отображаются в админке
    list_display = ('user', 'author')
    # Поля которые поддерживают поиск
    search_fields = ('user', 'author')
    # Поля, которые поддерживают фильтр
    list_filter = ('user', 'author')
    # Это свойство сработает для всех колонок: где пусто — там будет эта строка
    empty_value_display = '-пусто-'


# При регистрации модели Post конфигом для неё назначаемкласс PostAdmin
# А для регистрации модели Group - класс GroupAdmin
admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
