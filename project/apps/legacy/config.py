from django.apps import AppConfig


class LegacyConfig(AppConfig):
    name = 'apps.legacy'
    verbose_name = 'Legacy'

    def ready(self):
        return
