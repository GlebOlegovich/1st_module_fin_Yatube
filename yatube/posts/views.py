from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import GLOBAL_SETTINGS

from .forms import PostForm, CommentForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    ''' Функция для рендера главной страницы'''
    template = 'posts/index.html'

    posts = Post.objects.select_related('author', 'group').all()
    try:
        godleib_post = Post.objects.select_related('author', 'group').get(id=1)
    except:
        godleib_post = None

    # Показывать по 10 записей на странице.
    paginator = Paginator(posts, GLOBAL_SETTINGS['posts_on_page'])

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Последние обновления на сайте',
        'godleib_post': godleib_post,
    }
    return render(request, template, context)


def group_list(request, slug):
    '''
    View-функция для страницы сообщества (показывает посты группы)
    '''
    template = 'posts/group_list.html'

    cur_group = get_object_or_404(Group, slug=slug)

    posts_of_group = cur_group.posts.select_related('author').all()

    paginator = Paginator(posts_of_group, GLOBAL_SETTINGS['posts_on_page'])

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'group': cur_group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    '''
    Рендеринг страницы пользователя, с его постами
    '''
    template = 'posts/profile.html'

    cur_profile = get_object_or_404(User, username=username)
    profile_posts = cur_profile.posts.select_related('group').all()

    paginator = Paginator(profile_posts, GLOBAL_SETTINGS['posts_on_page'])

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    context = {
        'cur_profile': cur_profile,
        'page_obj': page_obj,
        'count_posts': paginator.count,
    }
    if request.user.is_authenticated:
        if request.user != cur_profile:
            following = Follow.objects.filter(
                user=request.user,
                author=cur_profile
            ).exists()
            context.update({'following': following})

    return render(request, template, context)


def post_detail(request, post_id):
    '''
    Рендеринг деталей поста с id = post_id
    '''
    template = 'posts/post_detail.html'

    post = get_object_or_404(Post, id=post_id)

    title = post.text[:30]
    author_posts_count = Post.objects.filter(author_id=post.author_id).count()
    context = {
        'post': post,
        'title': title,
        'author_posts_count': author_posts_count,
        'form': CommentForm(),
        'comments': post.comments.all()

    }
    return render(request, template, context)


@login_required
def create_post(request):
    '''
    Только для авторизованного пользователя!!!\n
    Рендеринг страницы создания поста, получение из request.POST
    текста поста и группы (опционально)\n
    В БД, в поле author будет записан юзер - под которым человек залогинен
    '''
    template = 'posts/create_post.html'
    context = {'title': 'Новый пост'}

    # DRY!, определяем форму один раз!
    form = PostForm(request.POST or None,
                    files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author_id = request.user.id
        post.save()
        return redirect('posts:profile', username=request.user)

    context.update({'form': form})
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    '''
    Только для авторизованного пользователя!!!\n
    Рендеринг страницы редактирования поста, c id = post_id
    '''
    template = 'posts/create_post.html'
    context = {'title': 'Редактировать пост'}

    cur_post = get_object_or_404(Post, id=post_id)

    # На всякий случай, если кто то захочет изменить чужой пост по id поста
    if request.user != cur_post.author:
        return redirect('posts:post_detail', post_id=post_id)

    # instance - если есть, то save() обновит переданную модель
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=cur_post)

    if not form.has_changed():
        return redirect('posts:post_detail', post_id=post_id)

    if form.is_valid():
        # default_storage.delete(cur_post.image)
        form.save()
        return redirect('posts:post_detail', post_id=post_id)

    context.update({'form': form,
                    'is_edit': True,
                    'post_id': post_id, })
    return render(request, template, context)


@login_required
def delete_post(request, post_id):
    '''
    Только для авторизованного пользователя!!!\n
    Удаление поста с id = post_id из БД
    '''
    template = 'posts/delete_post.html'
    cur_post = get_object_or_404(Post, id=post_id)
    # На всякий случай, если кто то захочет удалить чужой пост по id поста
    if request.user != cur_post.author:
        return redirect('posts:post_detail', post_id=post_id)
    cur_post.delete()
    return render(request, template, {'post_id': post_id})


@login_required
def add_comment(request, post_id):
    # Получите пост
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post_id = post_id
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def delete_comment(request, comment_id):
    cur_comment = get_object_or_404(Comment, id=comment_id)
    if request.user == cur_comment.author:
        cur_comment.delete()
    return redirect('posts:post_detail', post_id=cur_comment.post.id)


@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    template = 'posts/follow.html'

    # Трудный блок кода будет щас (для меня пока что)
    # Получаем моделю нашего юзера
    cur_user = request.user
    # Получаем, с помощью related_name, у кого он является
    # фоловером в модели Follow
    followings = cur_user.follower.all()
    # Получаем посты, у которых авторами являются те, на кого подписан юзер
    posts = Post.objects.filter(
        author__following__user=request.user).select_related('author', 'group')

    # Показывать по 10 записей на странице.
    paginator = Paginator(posts, GLOBAL_SETTINGS['posts_on_page'])

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Последние обновления среди тех, на кого вы подписаны',
        'followings': User.objects.filter(
            id__in=followings.values('author')).all()
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    if request.user.username != username:
        Follow.objects.get_or_create(
            user=request.user,
            author=User.objects.get(username=username)
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    get_object_or_404(
        Follow,
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:profile', username=username)
