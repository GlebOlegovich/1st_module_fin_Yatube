from django import forms

from .models import Post, Comment


class PostForm(forms.ModelForm):
    '''
    Форма для создания нового поста / редактирования существующего\n
    >>\n
    class Meta:\n
        model = Post\n
        fields = ('text', 'group')\n
    <<\n
    '''
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')

        # Убрал, т.к. добавил в models.py, но тут можно каждой форме свой
        # хелп написать

        help_texts = {
            'group': 'Можете выбрать,  а можете не выбирать группу,'
                     'это не обязательно.',
            'text': ' Введите текст Вашего поста.',
            'image': 'Можете загрузить изображение',
        }


class CommentForm(forms.ModelForm):
    '''
    Форма для создания нового комента
    '''
    class Meta:
        model = Comment
        fields = ('text',)
        help_text = {
            'text': 'Текст коментария',
        }
