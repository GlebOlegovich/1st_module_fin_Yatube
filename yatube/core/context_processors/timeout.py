from yatube.settings import GLOBAL_SETTINGS


def seconds(request):
    return {'my_timeout': GLOBAL_SETTINGS['timeout_for_chace']}
