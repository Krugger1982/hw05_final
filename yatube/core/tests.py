from http import HTTPStatus
from django.test import TestCase, override_settings


@override_settings(DEBUG=False)
class ViewTestClass(TestCase):

    def test_error_page_404(self):
        """ Попытка пройти на несуществующу страницу даст ошибку 404"""
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
