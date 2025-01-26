from django.db import models

class Donation(models.Model):
    name = models.CharField(max_length=100, help_text="Name of the donor")
    email = models.EmailField(help_text="Email address of the donor")
    message = models.TextField(blank=True, null=True, help_text="Optional message from the donor")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Donation amount in INR")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Time of donation")
    razorpay_payment_id = models.CharField(max_length=100, blank=True, help_text="Razorpay payment ID")

    def __str__(self):
        return f"{self.name} - ₹{self.amount}"
