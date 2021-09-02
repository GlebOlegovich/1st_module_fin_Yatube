from django.shortcuts import render


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользователской страницы 404 мы не станем
    return render(request, "errors/404_pro.html", {"path": request.path},
                  status=404)


def server_error(request):
    return render(request, 'errors/500.html', status=500)


def permission_denied(request, exception):
    return render(request, 'errors/403.html', status=403)


def csrf_failure(request, reason=''):
    return render(request, 'errors/403csrf.html')
