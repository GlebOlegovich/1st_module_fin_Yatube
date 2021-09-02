from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Post(models.Model):
    '''
    Модель постов\n
    text - текст без ограничения по длине\n
    pub_date - дата в формате DateTime (SQL),
    c автозаполнением текущей даты\n
    author - автор поста (ссылка на модель User, если удалить автора -
    удалятся и его посты: on_delete=models.CASCADE, related_name='posts')\n
    group - группа с которой связан пост (ссылка на модель Group, если удалить
    группу, посты авторов останутся: on_delete=models.SET_NULL, blank=True,
    null=True, related_name='posts')\n
    image - картинки (необязательное поле)
    Есть метод :  def __str__(self) -> str, он вернет text[:15]\n
    \n
    class Meta : ordering = ['-pub_date']
    '''
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Текст поста')
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, в которой будет пост'
    )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        # 'Картинка',
        # Аргумент upload_to указывает директорию,
        # в которую будут загружаться пользовательские файлы.
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
        help_text='Можете загрузить изображение.'
    )

    class Meta:
        ordering = ['-pub_date']
        app_label = 'posts'

        default_related_name = 'posts'

        verbose_name_plural = 'Посты'
        verbose_name = 'Пост'

    def __str__(self) -> str:
        return self.text[:15]


class Group(models.Model):
    '''
    Модель группы:\n
    title - текст, максимальной длинны 200\n
    slug - уникальный Slug адрес (ссылка в формате) группы, не может быть пуст,
    максимальная длина 100\n
    description - текст, без ограничения по длине\n
    Есть метод :  def __str__(self) -> str, он вернет title группы\n
    P.S.:
    “Slug” – это короткое название-метка, которое содержит только буквы, числа,
    нижнее подчеркивание или дефис. В основном используются в URL.\n
    '''
    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(
        unique=True, null=False,
        max_length=100,
        verbose_name='Ссылка на группу'
    )
    description = models.TextField(verbose_name='Описание сообщества')

    class Meta:
        app_label = 'posts'
        default_related_name = 'group'
        verbose_name_plural = 'Группы'

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    '''
    Модель коментариев к посту
    '''
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост, к которому комент',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор комента',
    )
    text = models.TextField(verbose_name='Текст комментария')
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления комента'
    )

    class Meta:
        ordering = ['-created']
        app_label = 'posts'

        default_related_name = 'comments'

        verbose_name_plural = 'Комментарии'

    def __str__(self) -> str:
        return self.text


class Follow(models.Model):
    '''
    Модель подписок\n
    Пользователь, который подписывается - user\n
    На кого подписывается - author
    '''
    # Пользователь, который подписывается
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь - кто подписан',
        related_name='follower'
    )
    # Не очень уверен в такой реализации, в БД будет много записей очень
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь - на кого подписан',
        related_name='following'
    )

    class Meta:
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                name='Follow_unique'
            ),
        ]

    def __str__(self):
        return f"{self.user} follows {self.author}"
