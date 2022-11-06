from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewClass(TestCase):
    """ Класс тестирует вью-функцию приложения """
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create(username='authorized')

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorised_client = Client()
        self.authorised_client.force_login(UsersViewClass.user)

    def test_pages_uses_correct_template_for_anonym_user(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/logged_out.html': reverse('users:logout'),
            'users/password_reset_form.html': reverse(
                'users:password_reset_form'
            ),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'
            ),
            'users/password_reset_complete.html': reverse('users:reset_done'),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template_for_authorised_user(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'users/password_change_form.html': reverse(
                'users:password_change'
            ),
            'users/password_change_done.html': reverse(
                'users:password_change_done'
            ),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorised_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
