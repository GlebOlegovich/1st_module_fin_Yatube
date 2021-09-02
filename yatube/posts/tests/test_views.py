from typing import List
import shutil
import tempfile
from django.conf import settings
from django.test import Client, TestCase, override_settings
from django import forms
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Comment, Follow, Group, Post

User = get_user_model()

# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# Для сохранения media-файлов в тестах будет использоваться
# временная папка TEMP_MEDIA_ROOT, а потом мы ее удалим


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsViewsTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='StasBasov')
        cls.uniqiekey = ', уникальный ключ: 1231312451'
        cls.group = Group.objects.create(
            title=f'teeest_Group{cls.uniqiekey}',
            slug='teeest_Group_slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        # Создаем записи (15 шт) в БД
        for i in range(1, 16):
            post_i = Post.objects.create(
                text=f'Текст_{i}{cls.uniqiekey}',
                author=cls.user,
                group=cls.group,
                # Для проверки добавления картинок
                image=SimpleUploadedFile(
                    name='small.gif',
                    content=small_gif,
                    content_type='image/gif'
                )
            )
            # Для проверки комментариев у поста
            if i == 13:
                for j in range(2):
                    Comment.objects.create(
                        post=post_i,
                        author=cls.user,
                        text=f'Комент_{j} к посту {i} - текст',
                    )
        cls.user_name_auth = User.objects.create_user(username='auth')
        # Пост от другого юзера
        Post.objects.create(
            text=f'Текст_поста_без_группы{cls.uniqiekey}',
            author=cls.user_name_auth,
        )

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
        self.authorized_client.force_login(PostsViewsTest.user)
        self.author_client = Client()
        self.author_client.force_login(PostsViewsTest.user_name_auth)
        self.guest_client = Client()
        # Удаляем все подписки
        Follow.objects.all().delete()

    def form_test(self, form_fields, response):
        ''' Функция, для тестирования форм '''
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_all_templates(self):
        """
        Проверяем правильность выбора шаблона, для каждой View,
        """
        group_slug = PostsViewsTest.group.slug
        user_username = PostsViewsTest.user.username
        test_post_id = Post.objects.get(
            text=f'Текст_5{PostsViewsTest.uniqiekey}').id
        templates = {
            #   шаблон                    reverse
            'posts/index.html': (reverse('posts:index'),),
            'posts/group_list.html': (
                reverse('posts:group_list', kwargs={'slug': group_slug}),
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': user_username}),
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', kwargs={'post_id': test_post_id}),
            ),
            'posts/create_post.html': (
                reverse('posts:create_post'),
                reverse('posts:post_edit', kwargs={'post_id': test_post_id}),
            ),
            'posts/follow.html': (reverse('posts:follow_index'),)

        }
        for template, reverse_names in templates.items():
            # posts/create_post.html - шаблон для двух страниц
            # Поэтому, сделаем еще один цикл
            for reverse_name in reverse_names:
                with self.subTest(reverse_name=reverse_name):
                    response = self.authorized_client.get(reverse_name)
                    self.assertTemplateUsed(response, template)
        # Отдельно проверяем удаление поста, для этого
        # создадим пост и потом удалим его, перейдя на стр удаления поста (get)
        post_for_delete = Post.objects.create(
            text=f'Текст_поста_для_удаления{PostsViewsTest.uniqiekey}',
            author=PostsViewsTest.user
        )
        response = self.authorized_client.get(
            reverse('posts:delete_post',
                    kwargs={'post_id': post_for_delete.id})
        )
        self.assertTemplateUsed(response, 'posts/delete_post.html')

    def test_index(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))

        # Проверяем посты со страницы есть ли среди постов в БД?
        for i in response.context['page_obj'].object_list:
            self.assertIn(i, Post.objects.all())

        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_pud_date_0 = first_object.pub_date
        post_group_0 = first_object.group
        post_image_0 = first_object.image

        last_post = Post.objects.get(text=f'Текст_поста_без_группы'
                                          f'{PostsViewsTest.uniqiekey}')
        # Первым элеменом будет последний пост!
        self.assertEqual(post_text_0, f'Текст_поста_без_группы'
                                      f'{PostsViewsTest.uniqiekey}')
        self.assertEqual(post_author_0, PostsViewsTest.user_name_auth)
        self.assertEqual(post_pud_date_0, last_post.pub_date)
        self.assertEqual(post_group_0, None)
        expected_image = Post.objects.filter(text=post_text_0).get().image
        self.assertEqual(post_image_0, expected_image)

        second_object = response.context['page_obj'][1]
        post_text_1 = second_object.text
        post_author_1 = second_object.author
        post_group_1 = second_object.group
        post_image_1 = second_object.image
        self.assertEqual(post_text_1, f'Текст_15{PostsViewsTest.uniqiekey}')
        self.assertEqual(post_author_1, PostsViewsTest.user)
        self.assertEqual(post_group_1, PostsViewsTest.group)
        # А можно ли как то сверить напрямую с small_gif
        expected_image = Post.objects.filter(text=post_text_1).get().image
        self.assertEqual(post_image_1, expected_image)

        title = response.context['title']
        self.assertEqual(title, 'Последние обновления на сайте')

    def test_group_list(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        group = PostsViewsTest.group

        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': group.slug})
        )
        # Проверяем посты со страницы принадлежат группе или нет?
        for i in response.context['page_obj'].object_list:
            self.assertIn(i, group.posts.all())

        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_pud_date_0 = first_object.pub_date
        post_image_0 = first_object.image
        # Проверять группу не буду, итак на страницы группы поста

        # Последний пост группы
        post_of_group = group.posts.all()[0]
        # Первым элеменом будет последний пост!
        self.assertEqual(post_text_0, post_of_group.text)
        self.assertEqual(post_author_0, post_of_group.author)
        self.assertEqual(post_pud_date_0, post_of_group.pub_date)
        expected_image = Post.objects.filter(text=post_text_0).get().image
        self.assertEqual(post_image_0, expected_image)

        group_from_view = response.context['group']
        self.assertEqual(group_from_view, group)

    def test_profile(self):
        """Шаблон profile сформирован с правильным контекстом."""

        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        # Проверяем посты от автора или нет?
        for i in response.context['page_obj'].object_list:
            self.assertIn(i, self.user.posts.all())

        first_object = response.context['page_obj'][0]
        post_text_0 = first_object.text
        post_author_0 = first_object.author
        post_group_0 = first_object.group
        post_image_0 = first_object.image

        self.assertEqual(post_text_0, f'Текст_15{PostsViewsTest.uniqiekey}')
        self.assertEqual(post_author_0, PostsViewsTest.user)
        self.assertEqual(post_group_0, PostsViewsTest.group)
        expected_image = Post.objects.filter(text=post_text_0).get().image
        self.assertEqual(post_image_0, expected_image)

        self.assertEqual(PostsViewsTest.user, response.context['cur_profile'])

        profil_posts = self.user.posts.all()
        self.assertEqual(
            profil_posts.count(),
            response.context['count_posts']
        )

        # Тест Following - из контекста
        # Должно быть False
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        following = Follow.objects.filter(
            user_id=PostsViewsTest.user_name_auth.id,
            author_id=PostsViewsTest.user.id
        ).exists()
        self.assertFalse(following)
        self.assertEqual(following, response.context['following'])

        # Теперь сделаем что бы было True
        Follow.objects.create(
            user_id=PostsViewsTest.user_name_auth.id,
            author_id=PostsViewsTest.user.id
        )
        response = self.author_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        following = Follow.objects.filter(
            user_id=PostsViewsTest.user_name_auth.id,
            author_id=PostsViewsTest.user.id
        ).exists()
        self.assertTrue(following)
        self.assertEqual(following, response.context['following'])

    def test_post_detail(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        # Рассмотрим, например, 13ый пост
        post_id = Post.objects.get(
            text=f'Текст_13{PostsViewsTest.uniqiekey}'
        ).id
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )

        post_from_view = response.context['post']
        post = get_object_or_404(Post, id=post_id)
        self.assertEqual(post_from_view, post)
        self.assertEqual(post_from_view.author, PostsViewsTest.user)
        self.assertEqual(post_from_view.group, PostsViewsTest.group)
        self.assertEqual(post_from_view.image, post.image)

        title_from_view = response.context['title']
        title = post.text[:30]
        self.assertEqual(title_from_view, title)

        author_posts_count_from_view = response.context['author_posts_count']
        author_posts_count = Post.objects.filter(author=post.author).count()
        self.assertEqual(author_posts_count_from_view, author_posts_count)

        form_fields = {
            'text': forms.CharField
        }
        self.form_test(form_fields, response)

        comments_from_view = response.context['comments']
        self.assertQuerysetEqual(
            comments_from_view,
            Comment.objects.filter(post_id=post_id).all(),
            # Важно!
            # https://coderoad.ru/17685023/Как-проверить-что-Django-QuerySets-равны
            transform=lambda x: x
        )

    def test_create_post(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:create_post'))

        title_from_view = response.context['title']
        self.assertEqual(title_from_view, 'Новый пост')

        form_fields = {
            # При создании формы поля модели типа TextField
            # преобразуются в CharField с виджетом forms.Textarea
            'text': forms.CharField,

            # На удивление, и так, и так работает, видимо
            # forms.ChoiceField это дочений объект
            # forms.models.ModelChoiceField, или что то в духе)

            # 'group': forms.ChoiceField,
            'group': forms.models.ModelChoiceField,
            'image': forms.ImageField,
        }
        self.form_test(form_fields, response)

    def test_post_edit(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        # Рассмотрим, например, 9ый пост
        post = Post.objects.get(text=f'Текст_9{PostsViewsTest.uniqiekey}')
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': post.id})
        )

        form_fields = {
            'text': (
                forms.CharField,
                post.text
            ),
            'group': (
                forms.ChoiceField,
                post.group.id
            ),
            'image': (
                forms.ImageField,
                post.image
            )
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected[0])

                # form is unbound but contains data
                # Здесь будут показаны значения в форме, по ключу value:
                form = response.context.get('form').initial[value]
                # Проверка, на наличие данных поста в форме
                # (мы же редактируем пост)
                self.assertEqual(form, form_fields[value][1])

        # Проверяем, как работает, если контекст поста не изменяется
        # Вроде бы верно работает))
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data={'text': post.text, 'group': post.group.id},
            follow=True
        )
        # тут проверяю, что все норм работает, если пост не изменен
        # Во вьюхе же сделано так, что если пост не изменен -
        # не делается никаких записей в БД, все остается, как есть
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': post.id})
        )

    def test_pagination(self):
        # функция, для получения респонза, для главной
        # страницы нету же аргументов никаких...
        def get_response(url: str, arg: List, page: int):
            '''
            url - страница для которой получаем response
            args - List с аргументами для вью функции, напрмимер: 'slug': slug
            page - номер страницы по пагинатору
            '''
            if not page:
                if arg[0] is None:
                    response = self.authorized_client.get(reverse(url))

                else:
                    response = self.authorized_client.get(
                        reverse(url, kwargs={f'{arg[0]}': f'{arg[1]}'})
                    )
            else:
                if arg[0] is None:
                    response = self.authorized_client.get(
                        reverse(url) + f'?page={page}'
                    )

                else:
                    response = self.authorized_client.get(
                        reverse(url, kwargs={f'{arg[0]}': f'{arg[1]}'})
                        + f'?page={page}'
                    )
            return response

        username = PostsViewsTest.user.username
        slug = PostsViewsTest.group.slug
        urls = {
            # Крайний элемент List (5ки и 6ка) - ожидаемое количество
            # постов на 2ой стрнице, по пагинатору
            'posts:index': [None, None, 6],
            'posts:group_list': ['slug', slug, 5],
            'posts:profile': ['username', username, 5],
        }
        for url, arg in urls.items():

            # Проверка первой страницы
            response = get_response(url, arg, 0)
            self.assertEqual(len(response.context['page_obj']), 10)
            # Проверяем вторую страницу
            response = get_response(url, arg, 2)
            self.assertEqual(len(response.context['page_obj']), int(arg[2]))

    def test_redirect_from_delete_post_and_post_edit_if_not_author(self):
        """
        Проверяем редирект, стороннего юзера, на просмотр поста,
        если он перейдет на редактирование/удаление чужого поста
        """
        post = Post.objects.get(author=self.user_name_auth)
        for reversed_name in ('posts:post_edit', 'posts:delete_post'):
            with self.subTest(reversed_name=reversed_name):
                response = self.authorized_client.get(
                    reverse(reversed_name, kwargs={'post_id': post.id}),
                    follow=True
                )
                self.assertRedirects(response, reverse(
                    'posts:post_detail', kwargs={'post_id': post.id})
                )

    def test_index_follow(self):
        """
        Посты ваших подписок вам видны, кто не подписан - не видит постов
        """
        #               auth                        StasBasov
        data = [PostsViewsTest.user_name_auth, PostsViewsTest.user]
        # Проверяем, что не подписаны
        cnt = Follow.objects.filter(
            user=data[0],
            author=data[1]
        ).exists()
        self.assertFalse(cnt)
        # Подписываемя на StasBasov
        Follow.objects.create(
            user=data[0],
            author=data[1]
        )
        # Проверяем от лица auth
        response = self.author_client.get(reverse('posts:follow_index'))
        last_post = response.context['page_obj'][0]
        expected = Post.objects.get(text=f'Текст_15{PostsViewsTest.uniqiekey}')
        self.assertEqual(last_post, expected)
        # Проверяем от лица StasBasov
        response = self.authorized_client.get(reverse('posts:follow_index'))
        # Проверим через подсчет текста, среди Post_obj
        posts = response.context['page_obj'].count('text')
        self.assertEqual(posts, 0)

    def test_follow_author(self):
        """ Тестируем возможность подписываться  """
        #               auth                        StasBasov
        data = [PostsViewsTest.user_name_auth, PostsViewsTest.user]

        # Подписываемя на StasBasov
        self.author_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': data[1]}),
            follow=True
        )
        cnt = Follow.objects.filter(
            user=data[0],
            author=data[1]
        ).exists()
        self.assertTrue(cnt)

    def test_unfollow_author(self):
        #               auth                        StasBasov
        data = [PostsViewsTest.user_name_auth, PostsViewsTest.user]

        # Добпвляем подписку на StasBasov
        Follow.objects.create(
            user=data[0],
            author=data[1]
        )
        # Отписываемся
        self.author_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': data[1]}),
            follow=True
        )
        cnt = Follow.objects.filter(
            user=data[0],
            author=data[1]
        ).exists()
        self.assertFalse(cnt)
