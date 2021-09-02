# from django.shortcuts import render

# Тут сделаю функция для кастомной страницы 404
# Надо разбираться, не работает!

'''def page_not_found_view(request, *args, **kwargs):
    template = 'errors/404.html'
    print('Мы тут')
    response = render_to_response(template)
    response.status_code = 404
    return response'''

# Это я пытаюсь сделать кастомную страницу 404, но сейчас
# (если сделать дебаг фолсом)
# При переходе на неизвестную стр (404) кидает вот что терминал
'''
 "GET /%D0%B0%D1%8B HTTP/1.1" 404 3490
 "GET /static/css_for_404/style.css HTTP/1.1" 404 3514
 "GET /static/css_for_404/respons.css HTTP/1.1" 404 3516
 "GET /static/js_for_404/modernizr.custom.js HTTP/1.1" 404 3523
 "GET /static/js_for_404/jquery.nicescroll.min.js HTTP/1.1" 404 3528
 "GET /static/images_for_404/404.png HTTP/1.1" 404 3515
 "GET /static/js_for_404/scripts.js HTTP/1.1" 404 3514
 "GET /static/images_for_404/404.gif HTTP/1.1" 404 3515
 "GET /static/js_for_404/modernizr.custom.js HTTP/1.1" 404 3523
 "GET /static/js_for_404/jquery.nicescroll.min.js HTTP/1.1" 404 3528
 "GET /static/js_for_404/scripts.js HTTP/1.1" 404 3514
'''


# не получается почему то выгрузить другие css итп
# Хотя в строке 25 файла 404.html выгружаю лого сайта, все работает
# def page_not_found_view(request, exception):
#     return render(request, "errors/404.html", {"path": request.path},
#                   status=404)
