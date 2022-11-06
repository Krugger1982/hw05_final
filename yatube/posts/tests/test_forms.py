import shutil
import tempfile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post

# временная папка (для тестов) хранения медиафайлов
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='authorized')
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_for_tests',
            description='Тестовое описание группы',
        )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает новый пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # С помощью ОРМ проверить - появился пост с ожидаемыми значениями полей
        latest_post = Post.objects.latest('id')
        self.assertEqual(latest_post.text, form_data['text'])
        self.assertEqual(latest_post.group, self.group)

    def test_post_editing(self):
        """ Проверка как работает редактирование поста"""
        post = Post.objects.create(
            text='Текст поста который будем редактировать',
            author=self.user,
            group=self.group,
        )
        post_id = post.id
        posts_count = Post.objects.count()
        response = self.authorised_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post_id})
        )
        # проверим что вызван правильный шаблон
        self.assertTemplateUsed(response, 'posts/post_create.html')
        new_data = {
            'text': 'Новый текст после редактирования',
            'group': '',
        }
        response = self.authorised_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post_id}),
            data=new_data,
            follow=True
        )
        # количество постов в БД не изменилось
        self.assertEqual(posts_count, Post.objects.count())
        # вызываем из БД этот (измененный) пост
        new_post = get_object_or_404(Post, pk=post_id)
        # проверяем атрибуты  поста
        # Текст поста изменился!
        self.assertEqual(new_post.text, new_data['text'])
        # Автор остался прежним
        self.assertEqual(new_post.author.id, self.user.id),
        # Указатель на группу - исчез
        self.assertIsNone(new_post.group)
        # Проверка что в списке постов группы наш пост исчез
        self.assertNotIn(new_post, self.group.posts.all())

    def test_post_form_labels(self):
        """ Проверка лейблов полей в форме."""
        text_label = PostsCreateFormTests.form.fields['text'].label
        group_label = PostsCreateFormTests.form.fields['group'].label
        self.assertEqual(text_label, 'Текст поста')
        self.assertEqual(group_label, 'Группа')

    def test_post_form_help_texts(self):
        """ Проверка параметра help_texts в форме"""
        text_help_text = PostsCreateFormTests.form.fields['text'].help_text
        group_help_text = PostsCreateFormTests.form.fields['group'].help_text
        self.assertEqual(text_help_text, 'Текст нового поста')
        self.assertEqual(
            group_help_text,
            'Группа, к которой будет относиться пост'
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormContentsPictureTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='authorized')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_for_tests',
            description='Тестовое описание группы',
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        # Создаем авторизованный клиент
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user)

    def test_create_post_contents_picture(self):
        """Валидная форма создает запись в Post с картинкой."""

        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый текст для поста с картинкой',
            'group': self.group.id,
            'image': uploaded,
        }
        # Отправляем POST-запрос
        response = self.authorised_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        ))
        # проверяем что объект появился в базе
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # С помощью ОРМ проверить - появился пост с ожидаемыми значениями полей
        latest_post = Post.objects.latest('id')
        self.assertEqual(latest_post.text, form_data['text'])
        self.assertEqual(latest_post.group, self.group)
        self.assertEqual(latest_post.image, 'posts/small.gif')


class PostFormsCommentsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='simple_user')
        cls.user2 = User.objects.create_user(username='post_author')
        cls.post = Post.objects.create(
            author=cls.user2,
            text='Тестовый пост'
        )

    def setUp(self):
        self.authorised_client = Client()
        self.authorised_client.force_login(self.user1)

    def test_comment_form_creates_entry_in_database(self):
        """ При сохранении валидной формы с комментарием от
            авторизованного пользователя, новый коммент появится в БД. """
        post = Post.objects.latest('id')
        comments_count = post.comments.count()
        comment_data = {'text': 'Тестовый комментарий от пользователя user1'}
        self.assertEqual(comments_count, post.comments.count())
        # Проверяем авторизованного пользователя
        self.authorised_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': f'{post.id}'}
            ),
            data=comment_data,
            follow=True,
        )
        # количество комментариев к посту изменилось на 1
        self.assertEqual(comments_count + 1, post.comments.count())
        latest_comment = Comment.objects.latest('id')
        self.assertEqual(latest_comment.text, comment_data['text'])
