from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework import routers

from TotumApp.views.api_auth_views import login_session, logout_session, current_user
from TotumApp.views.api_tenant_views import TenantViewSet
from TotumApp.views.api_user_views import UserViewSet

app_name = 'core'

router = routers.SimpleRouter()
router.register(r'users', UserViewSet, basename='users')
router.register(r'tenants', TenantViewSet, basename='tenants')

urlpatterns = [
    path('schema/', SpectacularAPIView.as_view(), name='schema.spec'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='core:schema.spec'), name='schema.swagger'),
    path('auth/login/', login_session, name='auth_login'),
    path('auth/logout/', logout_session, name='auth_logout'),
    path('auth/me/', current_user, name='auth_me'),

]

urlpatterns += router.urls
