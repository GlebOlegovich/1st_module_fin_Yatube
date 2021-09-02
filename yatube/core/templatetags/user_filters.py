from django import template

# В template.Library зарегистрированы все встроенные теги и фильтры шаблонов;
# добавляем к ним и наш фильтр.
register = template.Library()


@register.filter
def addclass(field, css):
    '''
    Функция (фильтр) для добавления атрибута класс, нужно для фронта\n
    return field.as_widget(attrs={'class': css})
    '''
    return field.as_widget(attrs={'class': css})
