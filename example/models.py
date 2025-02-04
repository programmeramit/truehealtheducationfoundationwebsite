from django.db import models
from django.utils.timezone import now

class Donation(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the donor")
    email = models.EmailField(help_text="Email address of the donor")
    message = models.TextField(blank=True, null=True, help_text="Optional message from the donor")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Donation amount in INR")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time of donation")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, help_text="Razorpay payment ID")

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"


class Volunteer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=14)
    address =  models.CharField(max_length=50)
    created_at = models.DateTimeField(default=now)  # ✅ Add this line

    def __str__(self):
        return self.name


class VolunteerApplication(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=14)
    address =  models.CharField(max_length=50)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name