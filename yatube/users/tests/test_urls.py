from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class UsersURLTests(TestCase):

    def setUp(self) -> None:
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_all_urls_for_anonimus(self):
        urls = {
            HTTPStatus.OK.value: (
                '/auth/signup/',
                '/auth/login/',
                '/auth/reset/done/',
                '/auth/logout/',
                '/auth/password_reset/',
                '/auth/password_reset/done/',
                # как проверить 'reset/<uidb64>/<token>/', я хз
                '/auth/reset/done/',
            ),
            HTTPStatus.FOUND.value: (
                '/auth/password_change/',
                '/auth/password_change/done/',
            )

        }
        for status_code, adresses in urls.items():
            for adress in adresses:
                with self.subTest(adress=adress):
                    response = self.guest_client.get(adress)
                    self.assertEqual(response.status_code, status_code)

    def test_urls_for_authorized(self):
        urls = {
            HTTPStatus.OK.value: (
                '/auth/password_change/',
                '/auth/password_change/done/',
            )
        }
        for status_code, adresses in urls.items():
            for adress in adresses:
                with self.subTest(adress=adress):
                    response = self.authorized_client.get(adress)
                    self.assertEqual(response.status_code, status_code)

    def test_templates_for_anonimus(self):
        """
        Проверяем, какие templates используются для urls
        """
        urls = {
            # template           adresses
            'users/login.html': ('/auth/login/',),
            'users/password_reset_complete.html': ('/auth/reset/done/',),
            'users/password_reset_done.html': ('/auth/password_reset/done/',),
            'users/password_reset.html': ('/auth/password_reset/',),
            'users/signup.html': ('/auth/signup/',),
            'users/logged_out.html': ('/auth/logout/',),
        }
        for template, addresses in urls.items():
            for adress in addresses:
                with self.subTest(adress=adress):
                    response = self.guest_client.get(adress)
                    self.assertTemplateUsed(response, template)

    def test_templates_for_authorized(self):
        urls = {
            # template           adresses
            'users/password_change_form.html': ('/auth/password_change/',),
            'users/password_change_done.html': ('/auth/password_change/done/',)
        }
        for template, addresses in urls.items():
            for adress in addresses:
                with self.subTest(adress=adress):
                    response = self.authorized_client.get(adress)
                    self.assertTemplateUsed(response, template)
