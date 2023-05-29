import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models

from TotumApp.models.base_models import HistoryModel, BaseModel


class TotumUser(BaseModel, HistoryModel, AbstractUser):
    email = models.EmailField(unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


class Tenant(BaseModel, HistoryModel):
    slug = models.CharField(max_length=255, null=False, blank=False)
    name = models.CharField(max_length=255, null=False, blank=False)
    users = models.ManyToManyField(TotumUser, related_name="tenants")


class ApiToken(BaseModel):
    user = models.ForeignKey(TotumUser, on_delete=models.DO_NOTHING, related_name="tokens")
    tenant = models.ForeignKey(Tenant, on_delete=models.DO_NOTHING)
    key = models.CharField(max_length=128, editable=False, unique=True, blank=False, null=False)
    expiry_date = models.DateTimeField(editable=False, blank=False, null=False)

    @property
    def is_valid(self):
        return self.tenant in self.user.tenants and datetime.datetime.now() < self.expiry_date
