# Generated by Django 4.1.3 on 2025-01-26 13:12

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('example', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, help_text='Time of donation'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='donation',
            name='razorpay_payment_id',
            field=models.CharField(blank=True, help_text='Razorpay payment ID', max_length=100),
        ),
        migrations.AlterField(
            model_name='donation',
            name='amount',
            field=models.DecimalField(decimal_places=2, help_text='Donation amount in INR', max_digits=10),
        ),
    ]
