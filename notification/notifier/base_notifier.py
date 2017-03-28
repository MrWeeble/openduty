from openduty.models import Incident

from django.template.defaultfilters import truncatechars


class BaseNotifier(object):
    short_name = 'default notifier'
    delete_on_send = True
    notifier_settings = []

    def __init__(self, config=None):
        if not config:
            config = {}
        self.__config = config

    def notify(self, notification):
        raise NotImplementedError

