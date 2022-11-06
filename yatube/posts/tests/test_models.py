from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        # cls.user - это переменная, которая содержит функцию
        # создающую тестового пользователя
        cls.user = User.objects.create_user(username='auth')
        # cls.group - это переменная, создающая тестовую группу
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание'
        )
        # cls.post - переменная, которая создает тестовый пост для проверки
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост,длина которого более 15 символов'
        )

    def test_models_have_correct_object_name(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        group = self.group
        # ожидаемые значения которые выведет метод __str__
        expected_names = {
            post: self.post.text[:15],
            group: self.group.title
        }
        for name_model, expected_value in expected_names.items():
            with self.subTest(name_model=name_model):
                self.assertEqual(str(name_model), expected_value)

    def test_post_verbose_names(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'автор',
            'group': 'Группа',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)
