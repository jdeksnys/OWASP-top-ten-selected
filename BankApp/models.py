from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import Permission



class CustomUserManager(BaseUserManager):
    def create_user(self, socSecNumber, password):
        user = self.model(SocSecNumber=socSecNumber, FailedLoginCount=0, IsBlocked=False, is_anonymous=False, is_authenticated=True, is_active=True)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, socSecNumber, password):
        user = self.create_user(socSecNumber, password)
        return user
    def get_by_natural_key(self, socSecNumber):
        return self.get(SocSecNumber=socSecNumber)

class Customer(AbstractBaseUser):
    REQUIRED_FIELDS = ["Id", "FailedLoginCount", "IsBlocked"]
    USERNAME_FIELD = "SocSecNumber"
    objects = CustomUserManager()

    is_authenticated = models.BooleanField(default=True)
    is_anonymous = models.BooleanField(default=False)
    FailedLoginCount = models.IntegerField(null=False, default=0)
    is_active=models.BooleanField(default=True)
    TimeLockedUntil = models.DateTimeField(null=True)
    IsBlocked = models.BooleanField(default=False)

    Id = models.AutoField(primary_key=True)
    FirstName = models.CharField(max_length=50)
    LastName = models.CharField(max_length=50)
    SocSecNumber = models.IntegerField(12, unique=True)


class Account(models.Model):
    Id = models.AutoField(primary_key=True)
    CustomerId = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False, to_field="Id")
    Name = models.CharField(max_length=50)
    Balance = models.FloatField(null=False)
    def validate_constraints(self):
        if self.Balance < 0:
            raise ValidationError("Error: Account balance cannot be negative")


class Permission(models.Model):
    Id = models.AutoField(primary_key=True)
    Code = models.CharField(max_length=50)


class CustomerPermissions(models.Model):
    CustomerId = models.ForeignKey(Customer, on_delete=models.CASCADE, null=False, to_field="Id")
    PermissionId = models.ForeignKey(Permission, on_delete=models.CASCADE, null=False, to_field="Id")