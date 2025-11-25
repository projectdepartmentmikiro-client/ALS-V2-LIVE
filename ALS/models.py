from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
import random
from django.db.models.signals import post_save
from django.dispatch import receiver

address = models.CharField(max_length=255, blank=True, null=True)


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=20, unique=True)
    cover_image = models.ImageField(upload_to="books/", blank=True, null=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class BorrowRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower_name = models.CharField(max_length=200)
    id_number = models.CharField(max_length=50)
    department = models.CharField(max_length=100)
    duration_days = models.PositiveIntegerField()
    borrowed_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    returned_at = models.DateTimeField(blank=True, null=True)
    photo = models.ImageField(upload_to="borrower/", blank=True, null=True)

  
    returned = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)
    otp_code = models.CharField(max_length=10, blank=True, null=True)  # OTP for return

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = self.borrowed_at + timedelta(days=self.duration_days)
        if not self.otp_code:
            self.otp_code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.borrower_name} borrowed {self.book.title}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(
        upload_to="profile_images/", blank=True, null=True
    )


@receiver(post_save, sender=User)
def ensure_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)
