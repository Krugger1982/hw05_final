from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AboutUrlClass(TestCase):
    """ Класс тестирующий url-ы приложения 'about' """

    def test_available_pages(self):
        """ Проверка доступности страниц."""
        pages_statuses = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for page, expected_status in pages_statuses.items():
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, expected_status)

    def test_about_urls_use_correct_templates(self):
        """ Проверка правильности шаблонов."""
        template_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for url, template_name in template_names.items():
            with self.subTest(url=url, template_name=template_name):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template_name)


class AboutViewClass(TestCase):
    """ Класс тестирует вью-функцию приложения """

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)
