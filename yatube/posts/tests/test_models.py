from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostsModelsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста!',
        )

        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Комент - текст',
        )

        cls.user_2 = User.objects.create_user(username='user_2')
        cls.follow = Follow.objects.create(user=cls.user, author=cls.user_2)

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostsModelsTest.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

        group = PostsModelsTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

        comment = PostsModelsTest.comment
        expected_object_name = comment.text
        self.assertEqual(expected_object_name, str(comment))

        expected_object_name = (f"{PostsModelsTest.user} follows "
                                f"{PostsModelsTest.user_2}")
        self.assertEqual(expected_object_name, str(PostsModelsTest.follow))

    def test_help_text_of_Post(self):
        """help_text и verbose name в полях совпадает с ожидаемым."""

        # Модель Post
        post = PostsModelsTest.post
        field_help_texts_and_verbose_name = {
            # поле     хелп текст    verbose_name
            'text': ['Текст поста', 'Текст поста'],
            'group': ['Группа, в которой будет пост', 'Группа'],
            'image': ['Можете загрузить изображение.', 'Картинка']
        }

        # кортеж `field` содержит ключи исходного словаря 
        # `ffield_help_texts_and_verbose_name`;
        # кортеж `expected_value` содержит значения исходного словаря
        # `field_help_texts и verbose_name`.
        for field, expected_value in field_help_texts_and_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value[0])
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value[1]
                )
