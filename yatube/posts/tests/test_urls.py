from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsURLsTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.uniqiekey = ', уникальный ключ: 1231312451'
        Group.objects.create(
            title=f'Тестовая группа{cls.uniqiekey}',
            slug='test-slug',
            description='Тестовое описание',
        )

    def setUp(self) -> None:
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем пользователя
        self.user = User.objects.create_user(username='HasNoName1231312451')
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Авторизуем автора поста
        self.author_client = Client()
        self.author_client.force_login(PostsURLsTest.author)
        # Что бы не хардкодить
        self.test_slug = Group.objects.get(
            title=f'Тестовая группа{PostsURLsTest.uniqiekey}'
        ).slug
        self.test_post = Post.objects.create(
            author=PostsURLsTest.author,
            text=f'Тестовый текст поста!{PostsURLsTest.uniqiekey}',
        )

    def test_all_urls_for_anonimus_page_status(self):
        """
        Тестируем статус всех страниц, для неавторизованного пользователя
        """
        urls = {
            '/': HTTPStatus.OK.value,
            f'/group/{self.test_slug}/': HTTPStatus.OK.value,
            f'/profile/{self.user}/': HTTPStatus.OK.value,
            # Тут пробую метод format
            '/posts/{}/'.format(self.test_post.id): HTTPStatus.OK.value,
            '/not_page/': HTTPStatus.NOT_FOUND.value,
            '/create/': HTTPStatus.FOUND.value,
            f'/posts/{self.test_post.id}/edit/': HTTPStatus.FOUND.value,
            f'/posts/{self.test_post.id}/delete/': HTTPStatus.FOUND.value,
        }
        for adress, status_code in urls.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress)
                self.assertEqual(response.status_code, status_code)

    def test_anonimus_redirect(self):
        """
        Проверка редиректа, неавторизованного пользователя, на LogIn
        """
        urls = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.test_post.id}/edit/': f'/auth/login/?next=/posts/'
                                                 f'{self.test_post.id}/edit/',
            f'/posts/{self.test_post.id}/delete/': f'/auth/login/?next=/posts/'
                                                   f'{self.test_post.id}/'
                                                   f'delete/',
        }
        for adress, redirect_to in urls.items():
            with self.subTest(adress=adress):
                response = self.guest_client.get(adress, follow=True)
                self.assertRedirects(response, (redirect_to))

    def test_post_create_edit_for_authorized(self):
        """
        Тестируем статус страницы создания поста, для авторизованного
        пользователя, и что недоступно редактирование поста от автора auth,
        идет редирект на просмотр этого поста
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

        response = self.authorized_client.get(
            '/posts/{}/edit/'.format(self.test_post.id)
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

        response = self.authorized_client.get(
            f'/posts/{self.test_post.id}/edit/', follow=True
        )
        self.assertRedirects(response, f'/posts/{self.test_post.id}/')

    def test_templates_for_all_urls(self):
        """
        Проверяем, какие templates используются для urls
        """
        urls = {
            # template           adresses
            'posts/index.html': ('/',),
            'posts/group_list.html': (f'/group/{self.test_slug}/',),
            'posts/profile.html': (f'/profile/{self.user}/',),
            'posts/post_detail.html': (f'/posts/{self.test_post.id}/',),
            'posts/create_post.html': ('/create/',
                                       f'/posts/{self.test_post.id}/edit/',),
            'posts/delete_post.html': (f'/posts/{self.test_post.id}/delete/',)
        }
        for template, addresses in urls.items():
            for adress in addresses:
                with self.subTest(adress=adress):
                    # Проверим от лица автора поста, что бы все страницы
                    # были доступны с верный шаблоном
                    response = self.author_client.get(adress)
                    self.assertTemplateUsed(response, template)

    # Вынес создание поста в SetUp, так что можем спокойно переходить
    # на стр удаления поста
    def test_post_edit_delete_for_author_page_status(self):
        """
        Тестируем статус страницы редактирования поста, удаления поста
        для автора поста
        """
        response = self.author_client.get(f'/posts/{self.test_post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

        response = self.author_client.get(
            f'/posts/{self.test_post.id}/delete/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_guest_follow_unfollow(self):
        """ Гость при попытке подписаться/отписаться получит страницу Login """
        urls = {
            'posts:profile_follow': '/auth/login/?next=/profile/auth/follow/',
            'posts:profile_unfollow': '/auth/login/?next=/profile/auth'
                                      '/unfollow/',
        }

        for url, slug in urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(
                    url,
                    kwargs={'username': PostsURLsTest.author}),
                    follow=True
                )
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
                self.assertRedirects(response, slug)
