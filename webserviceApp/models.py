from djongo import models
from bson import ObjectId
from django.contrib.auth.models import AbstractUser



# For Amdin, Provider and Client LogIn purpose -
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'admin'),
        ('provider', 'provider'),
        ('client', 'client'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='webserviceapp_users',
        blank=True,
        help_text="The groups this user belongs to."
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='webserviceapp_users_permissions',
        blank=True,
        help_text="Specific permissions for this user."
    )

    def __str__(self):
        return f"{self.username} - {self.role}"



#-----------------------------------------------------------------------------


# For the Provider Services -
class ProviderService(models.Model):

    _id = models.ObjectIdField(default=ObjectId, primary_key=True)

    SERVICE_TYPES = [
        ('plumbing', 'plumbing'),
        ('electrical', 'electrical'), 
    ]    

    name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=20, choices=SERVICE_TYPES)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Add image and video fields
    image = models.ImageField(upload_to='service_images/', blank=True, null=True)
    video = models.FileField(upload_to='service_videos/', blank=True, null=True)
    time_slot = models.CharField(max_length=20, blank=True, null=True)


    def __str__(self):
        return f"{self.name} - {self.get_service_type_display()}"
    

    class Meta:
        db_table='Provider_services'



class BookingHistory(models.Model):
    _id = models.ObjectIdField(default=ObjectId, primary_key=True)
    user_name = models.CharField(max_length=100)
    service_name = models.CharField(max_length=100)
    service_type = models.CharField(max_length=50)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_name} booked {self.service_name}"
    
    class Meta:
        db_table = "booking_history"