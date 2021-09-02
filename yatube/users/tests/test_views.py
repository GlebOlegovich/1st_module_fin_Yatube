from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewsTests(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='auth')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_all_templates(self):
        """
        Проверяем правильность выбора шаблона, для каждой View
        """

        templates = {
            #   шаблон                    reverse
            'users/login.html': reverse('users:login'),
            'users/signup.html': reverse('users:signup'),
            'users/password_change_form.html': reverse(
                'users:password_change_form'
            ),
            'users/password_change_done.html': reverse(
                'users:password_change_done'
            ),
            'users/password_reset.html': reverse('users:password_reset'),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'
            ),
            'users/password_reset_complete.html': reverse(
                'users:password_reset_complete'
            ),
            # Как быть с токеном, не знаю, откуда брать его...
            # 'users/password_reset_confirm.html': reverse(
            #     'users:password_reset_confirm'
            # ),
            'users/logged_out.html': reverse('users:logout'),
        }

        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_signup_context(self):
        """Шаблон signup сформирован с правильным контекстом."""

        response = self.authorized_client.get(reverse('users:signup'))

        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'first_name': forms.CharField,
            'last_name': forms.CharField,
            'username': forms.CharField,
            'email': forms.EmailField,
            # forms.PasswordInput не работает,
            # видимо, password преобразуется в CharField,
            # а как тогда проверить вообще, что пароль есть в форме?)
            'password1': forms.CharField,
            'password2': forms.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)
