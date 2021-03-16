from django.apps import AppConfig


class ApiSnConfig(AppConfig):
    name = 'api_sn'

    def ready(self):
        import api_sn.signals
