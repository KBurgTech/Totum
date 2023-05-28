from django.apps import AppConfig


class TotumappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TotumApp'

    def ready(self):
        from TotumApp.token_authentication import TokenAuthenticationScheme
