from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import BaseAuthentication

from TotumApp.models.auth_models import ApiToken


class TokenAuthentication(BaseAuthentication):

    def authenticate(self, request):
        try:
            t = ApiToken.objects.get(key=request.headers.get('X-API-Key', ''))
            return t.user, None
        except ApiToken.DoesNotExist:
            return None


class TokenAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = TokenAuthentication
    name = 'Totum API Auth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
        }
