from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from ..models import Post

User = get_user_model()


class ChacheTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.godleib = User.objects.create_user(username='Godleib')
        cls.uniqiekey = ', уникальный ключ: 1231312451'
        cls.post_1 = {'text': f'Текст post_1{cls.uniqiekey}', }
        cls.post_1_edited = {'text': f'Текст post_1_edited{cls.uniqiekey}', }

    def setUp(self) -> None:
        self.guest_client = Client()
        # Делаем первый пост
        self.post_1 = Post.objects.create(
            author=ChacheTest.godleib,
            text=ChacheTest.post_1['text'],
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(ChacheTest.godleib)

        cache.clear()

    def test_chache_index(self):
        """
        Тестируем кэш, главной страницы, он
        распространяется только на карточки постов
        """

        response = self.guest_client.get(reverse('posts:index'), )
        last_post = response.context['page_obj'][0]
        first_render = response.content
        # Проверка (что пост появился на главной стр), наверное и не нужна...
        self.assertEquals(last_post.text, ChacheTest.post_1['text'])

        # Изменяем пост
        post_1_edited = get_object_or_404(Post, text=ChacheTest.post_1['text'])
        post_1_edited.text = ChacheTest.post_1_edited['text']
        post_1_edited.save()

        response = self.guest_client.get(reverse('posts:index'), )
        # Сравниваем контент 1го рендеринга
        # и после изменения поста через запрос к БД
        self.assertEquals(first_render, response.content)

        cache.clear()

        # Делаем гет запрос новый (кэш пересоздастся)
        response = self.guest_client.get(reverse('posts:index'), )

        self.assertNotEquals(first_render, response.content)
