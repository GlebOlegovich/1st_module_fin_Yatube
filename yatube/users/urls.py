from django.contrib.auth import views
from django.contrib.auth.decorators import login_required
# Импортируем из приложения django.contrib.auth нужный view-класс
from django.contrib.auth.views import (LoginView, LogoutView,
                                       PasswordChangeView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView)
from django.urls import path

from . import views

app_name = 'users'


urlpatterns = [
    path(
        'logout/',
        # Прямо в описании обработчика укажем шаблон,
        # который должен применяться для отображения возвращаемой страницы.
        # Да, во view-классах так можно! Как их не полюбить.

        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),

    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),

    path('signup/', views.SignUp.as_view(), name='signup'),

    path(
        'password_change/',

        PasswordChangeView.as_view
        (template_name='users/password_change_form.html'),

        name='password_change_form'
    ),

    path(
        'password_change/done/',
        # Если пользователь не авторизован - перенаправит на LogIn
        # Все блягодаря login_required
        login_required(PasswordResetDoneView.as_view
                       (template_name='users/password_change_done.html')
                       ),

        name='password_change_done'
    ),

    path(
        'password_reset/',
        PasswordResetView.as_view(template_name='users/password_reset.html'),
        name='password_reset'
    ),

    path(
        'password_reset/done/',

        PasswordResetDoneView.as_view
        (template_name='users/password_reset_done.html'),

        name='password_reset_done'
    ),

    path(
        'reset/<uidb64>/<token>/',

        PasswordResetConfirmView.as_view
        (template_name='users/password_reset_confirm.html'),

        name='password_reset_confirm'
    ),

    path(
        'reset/done/',

        PasswordResetCompleteView.as_view
        (template_name='users/password_reset_complete.html'),

        name='password_reset_complete'
    ),
]
