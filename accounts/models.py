from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=30)
    program_study = models.ForeignKey(
        'api.ProgramStudy',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='roles'
    )

    def __str__(self):
        return self.name

    



# class UserManager(BaseUserManager):
#     use_in_migrations = True

#     def _create_user(self, id, password, **extra_fields):
#         """
#         Create and save a user with the given id and password.
#         """
#         if not id:
#             raise ValueError("The given ID must be set")
#         user = self.model(id=id, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_user(self, id, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", False)
#         extra_fields.setdefault("is_superuser", False)
#         return self._create_user(id, password, **extra_fields)

#     def create_superuser(self, id, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)

#         if extra_fields.get("is_staff") is not True:
#             raise ValueError("Superuser must have is_staff=True.")
#         if extra_fields.get("is_superuser") is not True:
#             raise ValueError("Superuser must have is_superuser=True.")

#         return self._create_user(id, password, **extra_fields)


class User(AbstractUser):
    # ROLE_CHOICES = (
    #     ('admin', 'Admin'),
    #     ('supervisor', 'Supervisor'),
    #     ('user', 'User'),
    # )

    SURVEY_CHOICES = (
        ('none', 'None'),
        ('exit', 'Exit'),
        ('lv1', 'Level 1'),
        ('lv2', 'Level 2'),
    )

    id = models.CharField(primary_key=True, max_length=50) #nim
    username = models.CharField("fullname", max_length=255)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    program_study = models.ForeignKey(
        'api.ProgramStudy',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='users'
    )
    address = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    last_survey = models.CharField(max_length=10, choices=SURVEY_CHOICES, default='none')


    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username} ({self.role})"


