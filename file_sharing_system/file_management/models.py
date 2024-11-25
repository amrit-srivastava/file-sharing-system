from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
import uuid

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('ops', 'Operations User'),
        ('client', 'Client User'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    email_verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4)

class File(models.Model):
    file = models.FileField(
        upload_to='uploads/',
        validators=[FileExtensionValidator(allowed_extensions=['pptx', 'docx', 'xlsx'])]
    )
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(auto_now_add=True)
    download_token = models.UUIDField(default=uuid.uuid4)