from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostUrlsTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='authorized')
        cls.user2 = User.objects.create(username='authorized2')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user2
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug_for_tests',
            description='Тестовое описание группы',
        )

    def setUp(self):
        # клиент для авторизованного пользователя
        self.authorized_client = Client()
        self.authorized_client.force_login(PostUrlsTests.user)

        # клиент для подключения автора
        self.author_client = Client()
        self.author_client.force_login(PostUrlsTests.user2)
        cache.clear()

    # Тестируем доступность страниц разным пользователям
    def test_available_pages_for_anonim_user(self):
        """ Страницы которые доступны неавторизованному пользователю"""
        pages_statuses = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user2.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
        }
        for page, expected_status in pages_statuses.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, expected_status)

    def test_redirected_pages_for_anonim_user(self):
        """ Страницы которые недоступны неавторизованному пользователю.
            Должны редиректить на страницу авторизации"""
        redirects = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit'
            '/': f'/auth/login/?next=/posts/{self.post.id}/edit/',
        }
        for page, expected_redirect in redirects.items():
            with self.subTest(
                required_page=page,
                expected_redirect=expected_redirect
            ):
                response = self.client.get(page)
                self.assertRedirects(response, expected_redirect)

    def test_available_pages_for_authorised_user(self):
        """ Страницы, доступные аворизованному пользователю"""
        pages_statuses = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
        }
        for page, expected_status in pages_statuses.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, expected_status)

    def test_redirected_pages_for_authorized_user(self):
        """ Страница редактирования поста должна редиректить авторизованного
            пользователя (не автора поста) на подробное описание этого поста
            без возможности редактирования."""
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_page_edit_post_is_available_for_its_author(self):
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    #  Проверка вызываемых HTML-шаблонов

    def test_posts_urls_use_correct_templates(self):
        """Страница по соответствующему адресу использует правильный шаблон."""
        template_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/post_create.html',
            f'/posts/{self.post.id}/edit/': 'posts/post_create.html',
        }
        # протестируем все страницы пользователем
        # у которого достаточно прав (автором поста)
        for url, template_name in template_names.items():
            with self.subTest(url=url, template_name=template_name):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                # если страница не рабочая, тест упадет на этом месте
                self.assertTemplateUsed(response, template_name)
