from django.contrib import admin
from django.db.models import Sum
from django.shortcuts import render
from datetime import date, datetime
from unfold.admin import ModelAdmin  # ✅ Correct import
from .models import Donation, Volunteer, VolunteerApplication



# ✅ Use `site.register` instead of `admin.register`
@admin.register(Donation)
class DonationAdmin(ModelAdmin):
    list_display = ("name", "email", "amount", "message")
    search_fields = ("name", "email")
    list_per_page=10
    def changelist_view(self, request, extra_context=None):
        # Get aggregated data for the chart
        total_donations = Donation.objects.aggregate(total_amount=Sum('amount'))['total_amount']
        total_donations_today = Donation.objects.filter(created_at=date.today()).aggregate(total_amount=Sum('amount'))['total_amount']
        total_donations_year = Donation.objects.filter(created_at__year=datetime.now().year).aggregate(total_amount=Sum('amount'))['total_amount']
        
        # Prepare chart data (you can add more categories like monthly donations)
        chart_data = {
            'total': total_donations or 0,
            'daily': total_donations_today or 0,
            'yearly': total_donations_year or 0
        }

        # Inject chart data into the context
        extra_context = extra_context or {}
        extra_context.update({
            'chart_data': chart_data
        })

        return super().changelist_view(request, extra_context=extra_context)


@admin.action(description="Approve and remove selected volunteers")
def approve_and_remove_volunteers(modeladmin, request, queryset):
    for application in queryset:
        if not application.is_approved:
            Volunteer.objects.create(
                name=application.name,
                email=application.email,
                phone_number=application.phone_number,
                address=application.address
            )
            application.delete()

@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(ModelAdmin):
    list_display = ('name', 'email', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('name', 'email')
    actions = [approve_and_remove_volunteers]
    list_per_page=10

@admin.register(Volunteer)
class VolunteerAdmin(ModelAdmin):
    list_per_page=10
    list_display = ('name', 'email')
    search_fields = ('name', 'email')
