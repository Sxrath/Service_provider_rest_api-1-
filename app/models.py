from django.utils import timezone
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_User = models.BooleanField(default=False)  
    is_service = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    balance=models.PositiveIntegerField(default=1000)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
   
    def __str__(self) -> str:
        if self.username:
           return self.username
        else:
          return self.email



class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Locations(models.Model):
    location = models.CharField(max_length=225)

    def __str__(self):
        return self.location

class ServiceProviderprofile(models.Model):
    user=models.ForeignKey(CustomUser,models.CASCADE)
    document=models.FileField()
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
    ph = models.CharField(validators=[phone_regex], max_length=17, blank=True,null=True)  # validators should be a list
    is_ok=models.BooleanField(default=False)
    def __str__(self) -> str:
        return f"profile of {self.user.username}"
    
class ServiceProvider(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100)
    location = models.ForeignKey(Locations, on_delete=models.CASCADE, default=None)
    description = models.TextField(blank=True)
    approve = models.BooleanField(default=False)
    avg_rating = models.FloatField(default=0)
    def __str__(self):
        return self.shop_name


class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now, blank=True)
 
class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    service = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    feedback = models.TextField()
    rating = models.IntegerField(null=False)
    def __str__(self) -> str:
        return f'{self.user} feedback on {self.service}'


def calculate_avg_rating(service_provider_id):
    feedbacks = Feedback.objects.filter(service__id=service_provider_id)
    total_ratings = feedbacks.aggregate(models.Avg('rating'))['rating__avg']
    return total_ratings if total_ratings is not None else 0

@receiver(post_save, sender=Feedback)
def update_avg_rating(sender, instance, **kwargs):
    service_provider = instance.service
    avg_rating = calculate_avg_rating(service_provider.id)
    service_provider.avg_rating = avg_rating
    service_provider.save()

# class CutomizedPackage(models.Model):
#     user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
#     package=models.TextField()
#     rate=models.PositiveIntegerField(default=1)
#     start=models.DateField()
#     end=models.DateField()
#     is_ended=models.BooleanField(default=False)
    
# class Post(models.Model):
#     user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
#     caption=models.CharField(max_length=100)
#     content=models.TextField()
#     photo=models.ImageField(upload_to='posts/')
#     created_at=models.DateTimeField(auto_now_add=True)

# class comment(models.Model):
#     user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
#     comment=models.TextField()
#     send_at=models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"From: {self.sender} - To: {self.receiver}"
    

class Payment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    payment = models.PositiveIntegerField(default=2000)  
    service = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE)
    cancelled = models.BooleanField(default=False)
    def __str__(self) -> str:
        return f"{self.user} payment on {self.service} booking"

    @receiver(post_save, sender=Booking)
    def create_payment_and_deduct_balance(sender, instance, created, **kwargs):
        if created:
            user = instance.user
            service = instance.service

            # Check if user has sufficient balance
            if user.balance >= 100:
                # Deduct 100 from user's balance
                user.balance -= 100
                user.save()

                # Create Payment object
                payment = Payment.objects.create(
                    user=user,
                    payment=100,  # Deducted amount
                    service=service
                )
            else:
                raise ValueError("Insufficient balance to make the booking.")

class Report(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    service=models.ForeignKey(ServiceProvider,on_delete=models.CASCADE)
    reason=models.TextField()
    def __str__(self) -> str:
        if self.user.username:
           return self.user.username
        else:
          return self.reason

class FeedbackRespond(models.Model):
    user=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    feedback=models.ForeignKey(Feedback,on_delete=models.CASCADE)
    respond=models.TextField()

    def __str__(self) -> str:
        return f"{self.user} responded to {self.feedback}"

