from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Create your models here.

class CommonFeatures(models.Model):

    class Meta:
        abstract = True  # This makes it an abstract base model

    @classmethod
    def can_be_featured(cls):
        # You can implement custom logic here to determine if the model can be featured.
        # For example, you can check a global setting or perform other checks.
        return True


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$', message="Please enter a valid phone number")
    phonenumber = models.CharField(
        validators=[phone_regex], max_length=17, blank=True, null=True)
    photoURL = models.URLField(blank=True, null=True)
    image = models.ImageField(null=True, blank=True,
                              default='/placeholder.png')
    last_login_device = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name