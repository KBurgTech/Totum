import random
import string

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, serializers, status, permissions
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response

from TotumApp.helper.serializers import SimpleResponseSerializer
from TotumApp.models.auth_models import TotumUser, ApiToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TotumUser
        fields = ['uuid', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}, 'uuid': {'read_only': True}}

    def create(self, validated_data):
        user = TotumUser(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)
        try:
            user.set_password(validated_data['password'])
            user.save()
        except KeyError:
            pass
        return user


class PasswordSerializer(serializers.Serializer):
    password = serializers.CharField()


class TokenRequestSerializer(serializers.Serializer):
    expiry_date = serializers.DateTimeField()
    tenant = serializers.UUIDField()


class TokenDeleteRequestSerializer(serializers.Serializer):
    id = serializers.UUIDField()


class TokenResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiToken
        fields = ['uuid', 'expiry_date', 'tenant', 'key']


class TotumUserPermissions(permissions.BasePermission):
    """
    Allows a user to only access their own user object
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that serializes Users
    """
    queryset = TotumUser.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'uuid'

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [IsAdminUser]
        elif self.action in (
                'retrieve', 'update', 'partial_update', 'destroy', 'set_password', 'create_api_token', 'get_api_tokens',
                'delete_api_token'):
            permission_classes = [TotumUserPermissions | IsAdminUser]
        else:  # Allow everyone to create a user
            permission_classes = [permissions.AllowAny]

        return [permission() for permission in permission_classes]

    @extend_schema(
        request=PasswordSerializer,
        responses={200: SimpleResponseSerializer},
        description="Change a users password",
        operation_id="users_set_password"
    )
    @action(detail=True, methods=['post'])
    def set_password(self, request: Request, uuid=None):
        user = self.get_object()
        if user != request.user:
            return Response({'message': 'You can only change your own password!'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user.set_password(serializer.validated_data['password'])
            user.save()
            return Response({'message': 'Password set'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        request=TokenRequestSerializer,
        responses={200: TokenResponseSerializer},
        description="Create an API Token for a user",
        operation_id="users_create_api_token"
    )
    @action(detail=True, methods=['post'])
    def create_api_token(self, request: Request, uuid=None):
        user = self.get_object()
        req_data = TokenRequestSerializer(data=request.data)
        req_data.is_valid(raise_exception=True)
        tenant = user.tenants.filter(uuid=req_data.validated_data['tenant']).first()
        if tenant is None:
            raise NotFound(f"Cannot find Tenant with id {req_data.validated_data['tenant']} for current user")

        token = ApiToken.objects.create(
            user=user,
            tenant=tenant,
            key=''.join(
                random.SystemRandom().choice(string.ascii_uppercase + string.digits + "!#+-*?$%&") for _ in range(128)),
            expiry_date=req_data.validated_data['expiry_date']
        )

        return Response(TokenResponseSerializer(token).data, status=201)

    @extend_schema(
        request=TokenRequestSerializer,
        responses={200: TokenResponseSerializer(many=True)},
        description="Get all tokens for a user",
        operation_id="users_get_tokens"
    )
    @action(detail=True, methods=['get'])
    def get_api_tokens(self, request: Request, uuid=None):
        user = self.get_object()
        return Response(TokenResponseSerializer(user.tokens.all(), many=True).data)

    @extend_schema(
        request=TokenDeleteRequestSerializer,
        responses={200: SimpleResponseSerializer},
        description="Delete a token for a user",
        operation_id="users_delete_token"
    )
    @action(detail=True, methods=['delete'])
    def delete_api_token(self, request: Request, uuid=None):
        user = self.get_object()
        req_data = TokenDeleteRequestSerializer(data=request.data)
        req_data.is_valid(raise_exception=True)
        token = user.tokens.get(uuid=req_data.validated_data['id'])
        if token is None:
            return NotFound(f"Cannot find Api Token with id {req_data.validated_data['id']} for current user")
        token.delete()
        return Response(SimpleResponseSerializer({"message": "Token deleted"}).data)
