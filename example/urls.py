# example/urls.py
from django.urls import path
from django.contrib.sitemaps.views import sitemap


from example.views import index,donate,payment_success,carrer,about_us,contact_us,privacy_policy,terms_condition,dashboard_callback,robots_txt,blog_detail,blog_list
from .sitemaps import BlogSitemap


urlpatterns = [
    path('', index,name="index"),
    path('donate/',donate,name="donate"),
    path('payment-success/<str:pay_id>', payment_success, name='payment_success'),
    path('carrer/',carrer,name="carrer"),
    path('about-us',about_us,name="about-us"),
    path('contact-us',contact_us,name="contact-us"),
    path('privacy-policy',privacy_policy,name="privacy-policy"),
    path("terms-condition",terms_condition,name="terms-condition"),
    path('blog/',blog_list,name="blog_list"),
    path('blog/<slug:slug>',blog_detail,name="blog_detail")

]

urlpatterns += [
    path('robots.txt', robots_txt, name='robots_txt'),
]
sitemaps = {
    'blog': BlogSitemap,
}

urlpatterns += [
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]