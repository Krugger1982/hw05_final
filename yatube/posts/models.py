from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """ Класс описывает таблицу сообществ (по группам авторов)."""
    # Название сообщества
    title = models.CharField(max_length=200)
    # название для адресной строки браузера
    slug = models.SlugField(unique=True)
    # Описание сообщества
    description = models.TextField()

    def __str__(self) -> str:
        # метод для вывода title при печати объекта
        return self.title


class Post(models.Model):
    """ Класс описывает таблицу для хранения постов."""
    # Текст поста
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    # Дата опубликования (можно использовать в фильтрах)
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    # поле "автор" - для связи с таблицей User
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    # Поле для связи с таблицей Group
    group = models.ForeignKey(
        Group,
        related_name='posts',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    # Аргумент upload_to указывает директорию,
    # в которую будут загружаться пользовательские файлы.

    class Meta:
        ordering = ['-pub_date']

    def __str__(self) -> str:
        # метод для вывода текста при печати объекта
        return self.text[:15]


class Comment(models.Model):
    """ Класс описывает таблицу для хранения комментариев к постам."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Оставьте комментарий'
    )
    # Время создания (можно использовать в фильтрах)
    created = models.DateTimeField(
        'Время публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ['-created']


class Follow(models.Model):
    """ Модель описывает таблицу для связи пользоветелей-подписчиков
        и их подписок.
    """
    # Тот, на которого подписались
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка'
    )
    # Подписчик
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
