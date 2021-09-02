from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CreationForm

User = get_user_model()


class UsersFormsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.signup_data = {
            'first_name': 'Polina',
            'last_name': 'Golovneva',
            'username': 'Polisha98',
            'email': 'pretty@woman.com',
            'password1': 'Test_password',
            'password2': 'Test_password'
        }

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_signup_form(self):
        # По идее, тут будет 0, но на всяк случ посчитаю
        users_count = User.objects.count()

        response = self.guest_client.post(
            reverse('users:signup'),
            data=self.signup_data,
            follow=True
        )

        # Проверяем кол-во юзеров
        self.assertEqual(users_count + 1, User.objects.count())

        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:index'))

    def test_help_text(self):
        """ Проверяет Help_text в форме CreationForm """
        expected = {
            'first_name': 'Введите Ваше имя',
            'last_name': 'Введите Вашу фамилию',
            'username': 'Введите Ваш никнэйм',
            'email': 'Введите Ваш email',
        }
        for value, expected_help_text in expected.items():
            with self.subTest(value=value):
                help_text = CreationForm.base_fields[value].help_text
                self.assertEquals(help_text, expected_help_text)

    def test_castom_validation_email(self):
        """ Проверяем кастомную валидацию email """
        # Симулируем регистрацию юзера
        self.guest_client.post(
            reverse('users:signup'),
            data=self.signup_data,
        )
        # Пробуем сделать повторную регистрацию
        # с тем же email
        form_2 = CreationForm(self.signup_data)
        self.assertFalse(form_2.is_valid())
        error = form_2.has_error('email', code='not_unique_email')
        self.assertTrue(error)
