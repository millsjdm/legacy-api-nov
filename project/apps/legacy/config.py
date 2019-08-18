from django.apps import AppConfig


class LegacyConfig(AppConfig):
    name = 'apps.legacy'
    verbose_name = 'Legacy Groups'

    def ready(self):
        return
