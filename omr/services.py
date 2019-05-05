import requests

from ldrawomr import settings

key = settings.REBRICKABLE_KEY


def get_set(set_num):
    url = 'http://rebrickable.com/api/v3/lego/sets/{}'.format(set_num)
    params = {'key': key}
    set_info = requests.get(url, params).json()
    return set_info


def get_theme(theme_id):
    url = 'http://rebrickable.com/api/v3/lego/themes/{}'.format(theme_id)
    params = {'key': key}
    theme_info = requests.get(url, params).json()
    return theme_info


def get_root_theme(theme_id):
    root_theme = theme_id
    while get_theme(root_theme).get('parent_id') is not None:
        root_theme = get_theme(root_theme).get('parent_id')

    return get_theme(root_theme)
