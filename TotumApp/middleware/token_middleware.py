from django.contrib import auth


class TokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token = request.headers.get('X-API-Key', '')
        user = auth.authenticate(token=token)
        if user:
            request.user = user

        response = self.get_response(request)
        return response
