from django.contrib.auth import get_user_model
import shutil
import tempfile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..forms import PostForm
from ..models import Comment, Group, Post

import random

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsFormsTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.godleib = User.objects.create_user(username='Godleib')
        cls.uniqiekey = ', уникальный ключ: 1231312451'
        cls.group = Group.objects.create(
            title='Тестовая группа_1',
            slug='test-slug_1',
            description='Тестовое описание Группы_1',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_post_1 = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.uploaded_post_for_edit_edited_text_and_image = SimpleUploadedFile(
            name='small_for_edit.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post_1 = {
            'text': f'Текст post_1{cls.uniqiekey}',
            'group': cls.group.id,
            'image': cls.uploaded_post_1
        }
        cls.post_for_edit_text = {
            'text': f'Текст поста, до изменения{cls.uniqiekey}',
            'group': cls.group.id,
        }
        cls.post_for_edit_edited_text_and_image = {
            'text': f'Текст поста, ПОСЛЕ изменения, и без группы'
                    f'{cls.uniqiekey}',
            'image': cls.uploaded_post_for_edit_edited_text_and_image
        }

        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Модуль shutil - библиотека Python с удобными инструментами
        # для управления файлами и директориями:
        # создание, удаление, копирование, перемещение, изменение папок, файлов
        # Метод shutil.rmtree удаляет директорию и всё её содержимое
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(PostsFormsTest.user)

        self.post_for_edit = Post.objects.create(
            author=PostsFormsTest.user,
            text=self.post_for_edit_text['text'],
            group_id=self.post_for_edit_text['group']
        )

        self.guest_client = Client()
        self.other_authorized_client = Client()
        self.other_authorized_client.force_login(PostsFormsTest.godleib)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=self.post_1,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user.username})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись по данным post_1
        self.assertTrue(
            Post.objects.filter(
                text=self.post_1['text'],
                group=self.post_1['group'],
                author=self.user,
                image='posts/small.gif'
            ).exists()
        )

    def test_post_edit(self):
        """Валидная форма имзеняет запись в Post."""
        # Как оказалось, каждый раз когда вызывается тест,
        # БД чистится, остается только то, что было в SetUpClass
        # или SetUp
        posts_count = Post.objects.count()

        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post_for_edit.id}
                    ),
            data=self.post_for_edit_edited_text_and_image,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': self.post_for_edit.id})
        )

        # Проверяем, НЕ увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)

        # Проверяем изменился ли текст поста
        post_edited = Post.objects.filter(
            text=self.post_for_edit_edited_text_and_image['text'],
            author=self.user,
            image='posts/small_for_edit.gif'
        )
        self.assertTrue(post_edited.exists())

        # Проверяем что группы теперь нет у поста
        self.assertEqual(post_edited.get().group, None)

    def test_delete_post(self):
        """ Удаляется ли пост? Проверим..."""
        # Создадим пост, для тестирования удаления
        post_for_delete = Post.objects.create(
            author=PostsFormsTest.user,
            text=f'Тестовый текст поста, но мы его удалим)!'
                 f'{PostsFormsTest.uniqiekey}',
        )
        posts_count = Post.objects.count()
        self.authorized_client.get(reverse(
            'posts:delete_post', kwargs={'post_id': post_for_delete.id},)
        )
        # Проверяем сколько теперь постов
        self.assertEqual(Post.objects.count(), posts_count - 1)

    def test_help_text(self):
        """ Проверяет Help_text в форме PostForm """
        expected = {
            'group': 'Можете выбрать,  а можете не выбирать группу,'
                     'это не обязательно.',
            'text': ' Введите текст Вашего поста.',
            'image': 'Можете загрузить изображение',
        }
        for value, expected_help_text in expected.items():
            with self.subTest(value=value):
                help_text = PostsFormsTest.form.fields[value].help_text
                self.assertEquals(help_text, expected_help_text)

    def test_comments_on_post_detail(self):
        '''
        Тут проверка:
            - комментировать посты может только авторизованный пользователь;
            - после успешной отправки комментарий появляется на странице поста.
        '''
        count_comments = Comment.objects.filter(
            post_id=self.post_for_edit.id).count()
        gona_make_comments = random.randint(2, 10)
        for i in range(gona_make_comments):
            self.other_authorized_client.post(
                reverse('posts:add_comment',
                        kwargs={'post_id': self.post_for_edit.id}
                        ),
                data={'text': f'Коментарий № {i}'},
                follow=True
            )
        gona_fail_comments = random.randint(2, 5)
        for _ in range(gona_fail_comments):
            self.guest_client.post(
                reverse('posts:add_comment',
                        kwargs={'post_id': self.post_for_edit.id}
                        ),
                data={'text': 'Коментарий, который не должен появиться!'},
                follow=True
            )
        self.assertEqual(
            Comment.objects.filter(post_id=self.post_for_edit.id).count(),
            count_comments + gona_make_comments
        )

        # Удаление коментария
        comment_for_delete = Comment.objects.get(
            post_id=self.post_for_edit.id,
            text=f'Коментарий № {random.randint(0, gona_make_comments-1)}',
        )
        self.other_authorized_client.get(
            reverse('posts:delete_comment',
                    kwargs={'comment_id': comment_for_delete.id}
                    )
        )
        self.assertEqual(
            Comment.objects.filter(post_id=self.post_for_edit.id).count(),
            count_comments + gona_make_comments - 1
        )
