from django.contrib.auth import authenticate, logout, login
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from TotumApp.helper.serializers import SimpleResponseSerializer
from TotumApp.views.api_user_views import UserSerializer


class LoginDataSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


@extend_schema(
    request=LoginDataSerializer,
    responses={200: SimpleResponseSerializer},
    description="Log a user in and create a session",
    operation_id="auth_login"
)
@api_view(['post'])
def login_session(request: Request):
    serializer = LoginDataSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = authenticate(request, username=serializer.data['email'], password=serializer.data['password'])
    if user is None:
        return Response({"message": "Username or password incorrect"})
    else:
        login(request, user)
        return Response({"message": "Success"})


@extend_schema(description="Log a user out and remove session", operation_id="auth_logout",
               responses={200: SimpleResponseSerializer})
@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def logout_session(request: Request):
    logout(request)
    return Response({"message": "Success"})


@extend_schema(description="Get the current user", operation_id="auth_me", responses={200: UserSerializer})
@api_view(['get'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request: Request):
    return Response(UserSerializer(request.user).data)
