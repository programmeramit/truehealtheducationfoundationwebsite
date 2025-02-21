import json
from django.contrib import admin
from django.urls import path
from django.db.models import Sum,Count
from django.utils.timezone import now, localdate
from django.views.generic import TemplateView
from django.utils.timezone import now, localdate, timedelta

from unfold.admin import ModelAdmin
from unfold.views import UnfoldModelAdminViewMixin

from .models import Donation, Volunteer, VolunteerApplication
from .utlis import send_certificate_email

logo_path ="https://res.cloudinary.com/dplbdop3n/image/upload/v1737955474/logo_l00s7s.png"


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
            send_certificate_email(
                receiver_email=application.email,
                volunteer_name=application.name,
                logo_path=logo_path,
                sender_email="support@truehealtheducationfoundation.org",
                sender_password="@Support48096"
            )


            
            application.delete()
        


@admin.register(Donation)
class DonationAdmin(ModelAdmin):
    list_display = ("name", "email", "amount", "message")
    search_fields = ("name", "email")
    list_per_page = 10


@admin.register(VolunteerApplication)
class VolunteerApplicationAdmin(ModelAdmin):
    list_display = ('name', 'email', 'is_approved')
    list_filter = ('is_approved',)
    search_fields = ('name', 'email')
    list_per_page = 10
    actions = [approve_and_remove_volunteers]



@admin.register(Volunteer)
class VolunteerAdmin(ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')
    list_per_page = 10


# Custom Dashboard View
admin.site.index_title = 'True Health Education Foundation'



class DashboardView(UnfoldModelAdminViewMixin, TemplateView):
    title = "True Health Education Foundation"
    permission_required = ()
    template_name = "admin/index.html"


class DashboardAdmin(ModelAdmin):
    def get_urls(self):
        return super().get_urls() + [
            path(
                "index",
                DashboardView.as_view(model_admin=self),
                name="index"
            ),
        ]


def dashboard_callback(request, context):
    # Fetch donation statistics and convert Decimal to float
    total_donations = float(Donation.objects.aggregate(total_amount=Sum('amount'))['total_amount'] or 0)
    total_donations_today = float(Donation.objects.filter(created_at=localdate()).aggregate(total_amount=Sum('amount'))['total_amount'] or 0)
    total_donations_year = float(Donation.objects.filter(created_at__year=now().year).aggregate(total_amount=Sum('amount'))['total_amount'] or 0)

    # Get volunteer trends (Last 7 Days)
    last_7_days = [(localdate() - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]
    volunteer_counts = [
        Volunteer.objects.filter(created_at__date=day).count() for day in last_7_days
    ]

    # Get donation trends (Last 7 Days)
    donation_counts = [
        float(Donation.objects.filter(created_at__date=day).aggregate(total_amount=Sum('amount'))['total_amount'] or 0)
        for day in last_7_days
    ]
    
    # Prepare data for donation chart (Donation amounts over the last 7 days)
    donation_chart_data = json.dumps({
        'datasets': [{'data': donation_counts, 'borderColor': 'rgb(75, 192, 192)', 'label': 'Donations'}],
        'labels': last_7_days
    })

    # Prepare volunteer chart data
    volunteer_chart_data = json.dumps({
        'datasets': [{'data': volunteer_counts, 'borderColor': 'rgb(54, 162, 235)', 'label': 'Volunteers'}],
        'labels': last_7_days
    })

    # Fetch recent donations (Last 5)
    recent_donations = Donation.objects.all().order_by('-created_at')[:5]
    recent_donations_data = [
        {"name": donation.name, "email": donation.email, "amount": float(donation.amount), "date": donation.created_at.strftime("%Y-%m-%d")}
        for donation in recent_donations
    ]

    # Fetch recent volunteers (Last 5)
    recent_volunteers = Volunteer.objects.all().order_by('-id')[:5]
    recent_volunteers_data = [
        {"name": volunteer.name, "email": volunteer.email, "joined": volunteer.created_at.strftime("%Y-%m-%d")}
        for volunteer in recent_volunteers
    ]

    # Pass all this data to the context
    context.update({
        "kpis": [
            {"title": "Total Donations", "metric": f"₹{total_donations}"},
            {"title": "Today's Donations", "metric": f"₹{total_donations_today}"},
            {"title": "Donations This Year", "metric": f"₹{total_donations_year}"},
            {"title": "Total Volunteers", "metric": Volunteer.objects.count()},
        ],
        "donationChartData": donation_chart_data,
        "volunteerChartData": volunteer_chart_data,
        "recentDonations": recent_donations_data,
        "recentVolunteers": recent_volunteers_data,
    })

    return context
