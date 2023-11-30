from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.
class Commodity(models.Model):
    date = models.DateField()
    commodity_name = models.CharField(max_length=100)
    minimum_price = models.PositiveIntegerField()
    maximum_price = models.PositiveIntegerField()
    average_price = models.PositiveIntegerField()

    class Meta:
        db_table = "Commodity_table"

class CustomAccountManager(BaseUserManager):
    def create_user(self, firstname=None, lastname=None, email=None, password=None):
        user = self.model(firstname=firstname, lastname=lastname, email=email, password=password)
        user.set_password(password)
        # user.is_staff = True
        user.is_superuser = False
        user.save(using=self._db)
        return user
    
    def create_superuser(self, firstname=None, lastname=None, email=None, password=None):
        user = self.create_user(firstname=firstname, lastname=lastname, email=email, password=password)
        user.is_active = True
        # user.is_staff = True
        user.is_superuser = True
        user.is_Admin = True
        user.save(using=self._db)
        return user
    
    def get_by_natural_key(self, email_):
        print(email_)
        return self.get(email=email_)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    firstname = models.CharField(max_length=100, null=True)
    lastname = models.CharField(max_length=100, null=True)
    email = models.EmailField(unique=True)
    is_admin = models.BooleanField(default=False)
    USERNAME_FIELD =  'email'

    objects = CustomAccountManager()

    # short name for each available user
    def get_short_name(self): 
        return self.email
    
    # user need to signin
    def natural_key(self):
        return self.email

    def __str__(self):
        return self.email
    
    @property
    def is_staff(self):
        return self.is_admin