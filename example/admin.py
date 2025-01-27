from django.contrib import admin

# Register your models here.
from .models import Donation
from .models import Volunteer, VolunteerApplication
from django.contrib.admin import AdminSite

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "amount", "message")
    search_fields = ("name", "email")

@admin.action(description="Approve and remove selected volunteers")
def approve_and_remove_volunteers(modeladmin, request, queryset):
    for application in queryset:
        if not application.is_approved:
            # Create a new Volunteer from the application
            Volunteer.objects.create(
                name=application.name,
                email=application.email,
                phone_number=application.phone_number,
                address=application.address
            )
            # Delete the application after approving
            application.delete()



@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('name', 'email')
    actions = [approve_and_remove_volunteers]


@admin.register(Volunteer)
class VolunteerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

