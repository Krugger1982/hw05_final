from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersUrlsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='authorized')

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(UsersUrlsTest.user)

    def test_available_pages_for_NonAuthorised_user(self):
        """ Страницы которые доступны неавторизованному пользователю"""
        pages_statuses = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
        }
        for page, expected_status in pages_statuses.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, expected_status)

    def test_redirected_pages_for_anonim_user(self):
        """ Страницы которые недоступны неавторизованному пользователю.
            Должны редиректить на страницу авторизации"""
        redirects = {
            '/auth/password_change/': (
                '/auth/login/'
                '?next=/auth/password_change/'
            ),
            '/auth/password_change_done/': (
                '/auth/login/'
                '?next=/auth/password_change_done/'
            ),
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
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change_done/': HTTPStatus.OK,
        }
        for page, expected_status in pages_statuses.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, expected_status)

    def test_posts_users_use_correct_templates(self):
        """Страница по адресу использует правильный шаблон."""
        template_names = {
            # тут важна очередность проверки страниц
            # после страницы logout не должно идти страниц, требующих
            # авторизации
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change_done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            # Страницу '/auth/password_reset_confirm пока тестировать не будем,
            # так как непонятно где брать токен
            '/auth/reset/done/': 'users/password_reset_complete.html',
        }
        # протестируем все страницы пользователем
        # у которого достаточно прав
        for url, template_name in template_names.items():
            with self.subTest(url=url, template_name=template_name):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                # если страница не рабочая, то тест упадет здесь
                self.assertTemplateUsed(response, template_name)
