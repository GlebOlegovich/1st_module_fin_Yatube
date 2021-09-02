from http import HTTPStatus

from django.test import TestCase


class CoreTests(TestCase):

    def test_error_pages(self):
        urls = {
            # страница          ошибка, шаблон
            '/nonexist-page/': [HTTPStatus.NOT_FOUND,
                                'errors/404_pro.html'],
        }
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, urls[url][0])
                self.assertTemplateUsed(response, urls[url][1])
