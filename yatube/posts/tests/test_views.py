from http import HTTPStatus
import shutil
import tempfile

from django import forms
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import (Comment, Group, Post, Follow)

User = get_user_model()
NUMBER_OF_PAGINATED_POSTS = settings.PAGINATION_COUNT + 2
# временная папка (для тестов) хранения медиафайлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        # в шаблон передан контекст с правильным объектом
        self.assertEqual(
            response.context['current_post'].text,
            self.post.text
        )
        self.assertEqual(
            response.context['current_post'].author.id,
            self.user.id
        )
        self.assertEqual(
            response.context['current_post'].id,
            self.post.id
        )


class PostViewsBigPagesTest(TestCase):
    """ Класс для проверки страниц, содержащих список элементов(постов).
        К таким страницам обычно подключается пагинатор."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        for i in range(NUMBER_OF_PAGINATED_POSTS):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост № {i+1} для проверки',
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_context_and_paginator_index_page(self):
        """ Шаблон главной страницы (с многими постами) сформирован
            с правильной пагинацией и правильным содержимым словаря
            context.
        """
        page_args = {
            'posts:index': {},
            'posts:profile': {'username': self.user.username},
            'posts:group_list': {'slug': self.group.slug},
        }
        for page, keyw in page_args.items():
            # вызываем первую пачку постов в шаблоне
            response = self.authorized_client.get(reverse(page, kwargs=keyw))
            first_post = response.context['page_obj'].object_list[0]
            self.assertEqual(
                first_post.text,
                f'Тестовый пост № {NUMBER_OF_PAGINATED_POSTS} для проверки'
            ),
            self.assertEqual(first_post.author.username, 'auth'),
            self.assertEqual(first_post.group.title, self.group.title)
            self.assertEqual(
                len(response.context['page_obj'].object_list),
                settings.PAGINATION_COUNT
            )
            # вызываем вторую "пачку" постов
            response = self.authorized_client.get(
                reverse('posts:index') + '/?page=2',
                kwargs=keyw
            )
            self.assertEqual(len(response.context['page_obj'].object_list), 2)


class PostViewsCreationEditionTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='simple_user')
        cls.user2 = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.another_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2'
        )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user1)
        self.author_client = Client()
        self.author_client.force_login(self.user2)

    def test_creating_post(self):
        """Проверка работы механизма создания поста ."""
        posts_count = Post.objects.count()
        response = self.authorised_client.get(reverse('posts:post_create'))
        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected_type in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected_type)
        self.assertEqual(response.context['is_edit'], False)
        #  заполним форму.
        post_data = {
            'text': 'текст поста для сохранения',
            'author': self.user2,
            'group': self.group.id
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            post_data,
            follow=True,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count + 1)

        # После успешного добавления поста в БД
        # проверяем как он отображается на разных страницах.
        page_args = {
            'posts:index': {},
            'posts:profile': {'username': self.user2.username},
            'posts:group_list': {'slug': self.group.slug},
        }
        for page, keyw in page_args.items():
            response = self.authorised_client.get(reverse(page, kwargs=keyw))
            first_post = response.context['page_obj'].object_list[0]
            self.assertEqual(first_post.text, post_data['text']),
            self.assertEqual(first_post.author.id, post_data['author'].id),
            self.assertEqual(first_post.group.id, post_data['group'])
            # Проверка - в списке постов второй группы нашего поста нет
            self.assertNotIn(
                get_object_or_404(Post, pk=first_post.id),
                self.another_group.posts.all()
            )

    def test_post_editing(self):
        """ Проверка как работает редактирование поста"""
        post = Post.objects.create(
            text='Текст поста который будем редактировать',
            author=self.user2,
            group=self.group,
        )
        post_id = post.id
        posts_count = Post.objects.count()
        response = self.author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        self.assertTemplateUsed(response, 'posts/post_create.html')
        new_data = {
            'text': 'Новый текст после редактирования',
            'group': '',
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=new_data,
            follow=True
        )
        # количество постов в БД не изменилось
        self.assertEqual(posts_count, Post.objects.count())
        # пост изменился на страницах index и profile
        page_args = {
            'posts:index': {},
            'posts:profile': {'username': self.user2.username},
        }
        for page, keyw in page_args.items():
            response = self.authorised_client.get(reverse(page, kwargs=keyw))
            post = response.context['page_obj'].object_list[0]
            # Текст поста изменился!
            self.assertEqual(post.text, new_data['text'])
            # Автор остался прежним
            self.assertEqual(post.author.id, self.user2.id),
            # Указатель на группу - исчез
            self.assertIsNone(post.group)
        # в списке постов группы наш пост исчез
        post = get_object_or_404(Post, pk=post_id)
        self.assertNotIn(post, self.group.posts.all())


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsPictureTest(TestCase):
    """ Класс для проверки как отображаются и создаются посты с картинками."""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копир-е, перемещ-е, изм-е папок и файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)
        # это тестовая картинка
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        # Это объект для записи картинки в БД
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        # Создаем запись в БД
        Post.objects.create(
            author=self.user,
            text='Текст для поста с картинкой длиной более 15 символов',
            image=uploaded,
            group=self.group,
        )

    def test_creating_post_contents_picture(self):
        """Проверка как работает вызов поста с картинкой."""

        # проверяем как он отображается в словаре context разных страниц.
        # на странице с подробным описанием одного поста
        post = Post.objects.latest('id')
        response = self.authorised_client.get(reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id}
        ))
        self.assertEqual(
            response.context['current_post'].image,
            'posts/small.gif'
        )
        # На страницах со списками постов
        page_args = {
            'posts:index': {},
            'posts:profile': {'username': self.user.username},
            'posts:group_list': {'slug': self.group.slug},
        }
        for page, keyw in page_args.items():
            response = self.authorised_client.get(reverse(page, kwargs=keyw))
            current_post = response.context['page_obj'].object_list[0]
            self.assertEqual(current_post.image, 'posts/small.gif')


class PostViewsCommentsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='simple_user')
        cls.user2 = User.objects.create_user(username='post_author')
        cls.post = Post.objects.create(
            author=cls.user2,
            text='Тестовый пост'
        )
        cls.comment = Comment.objects.create(
            author=cls.user1,
            post=cls.post,
            text='Тестовый комментарий'
        )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user1)

    def test_comment_displayed_correctly(self):
        """ Проверка отображения комментария на странице post_detail"""
        post = Post.objects.latest('id')
        response = self.client.get(
            reverse('posts:post_detail', kwargs={'post_id': f'{post.id}'})
        )
        # Проверяем как отдается комментарий
        self.assertIn(self.comment, response.context['comments'])


class PostTemlatesCacheTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='simple_user')
        cls.user1 = User.objects.create_user(username='simple_user1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            author=cls.user1,
            post=cls.post,
            text='Тестовый комментарий',
        )

    def setUp(self):
        cache.clear()

    def test_cache_index_page(self):
        """ Проверка кеширования списка постов на главной странице """
        response = self.client.get(reverse('posts:index'))
        Post.objects.create(
            author=self.user1,
            text='Тестовый пост для проверки кэширования',
        )
        # проверка сразу после добавления поста в БД
        # страница не изменилась, данные поступают из кэша
        response_cached = self.client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_cached.content)


class PostViewFollowTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user_author = User.objects.create_user(username='post_author')
        cls.user1 = User.objects.create_user(username='simple_user')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый текст № 1'
        )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user1)

    def test_authorised_user_can_follow(self):
        # В начале - отсутствует запись в таблице Follow
        self.assertFalse(
            Follow.objects.filter(
                user=self.user1,
                author=self.user_author
            ).exists()
        )
        response = self.authorised_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': 'post_author'}
            )
        )
        # проверяем как создалась запись в таблице Follow
        self.assertTrue(
            Follow.objects.filter(
                user=self.user1,
                author=self.user_author
            ).exists()
        )
        # Проверяем редирект
        self.assertRedirects(response, '/profile/post_author/')
        # На странице "избранные авторы" должен появиться пост автора
        response = self.authorised_client.get(reverse('posts:follow_index'))
        self.assertIn(self.post, response.context['page_obj'].object_list)

    def test_authorised_following_user_can_unfollow(self):
        # Создается изначальная связь в таблице Follow
        Follow.objects.get_or_create(
            user=self.user1,
            author=self.user_author,
        )
        response = self.authorised_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': 'post_author'}
            )
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user1,
                author=self.user_author
            ).exists()
        )
        self.assertRedirects(response, '/profile/post_author/')
        # На странице "избранные авторы" должен отсутствовать пост автора
        response = self.authorised_client.get(reverse('posts:follow_index'))
        self.assertNotIn(self.post, response.context['page_obj'].object_list)
