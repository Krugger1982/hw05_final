from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class UsersCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем форму, если нужна проверка атрибутов
        cls.form = CreationForm()

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()

    def test_create_new_user(self):
        """Валидная форма создает нового пользователя."""
        # Подсчитаем количество существующих пользователей
        users_count = User.objects.count()
        # Подготавливаем данные для передачи в форму
        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'Unknown',
            'email': 'noemail@gmail.com',
            # Важно! пароль должен пройти валидацию
            # нужно придумывать сильный пароль для тестов
            'password1': '#goodpassword1111',
            'password2': '#goodpassword1111',
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # Проверяем, увеличилось ли число пользователей
        self.assertEqual(User.objects.count(), users_count + 1)
        # проверка атрибутов последнего пользователя
        new_user = User.objects.latest('id')
        self.assertEqual(new_user.username, 'Unknown')
        self.assertEqual(new_user.first_name, 'Имя')
        self.assertEqual(new_user.last_name, 'Фамилия')
