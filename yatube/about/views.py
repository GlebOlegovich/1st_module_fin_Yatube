from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно произвести какие-то действия для создания контекста.
        # Для примера в словарь просто передаются две строки
        context['author_title'] = 'Это страница обо мне, а кто я такой??!'
        context['author_text'] = ('В общем, я Глеб, но называйте меня '
                                  'Godleib\n'
                                  'Я Студент 20ой когорты Япрактикума по '
                                  'бэкенду!\n'
                                  'Тут клаааааасно!')
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
