from django.urls import path

from deals.views.deals import deals, generate_deals

urlpatterns = [
    path('', deals, name='deals'),
    path('generate/', generate_deals, name='generate_deals'),
]