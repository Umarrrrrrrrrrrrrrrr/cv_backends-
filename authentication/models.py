import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom User model matching pgAdmin database schema"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255, blank=False, null=False)
    username = models.CharField(max_length=50, unique=True)
    # password is handled by AbstractUser (stored as password_hash in database)
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=50, default='user')
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        # Update last_login_at when user logs in
        if self.last_login:
            self.last_login_at = self.last_login
        super().save(*args, **kwargs)